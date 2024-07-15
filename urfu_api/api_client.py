from aiohttp import ClientSession
import asyncio
from random import uniform, choice
from typing import Optional, Union, Any, Protocol
from config import IS_DEBUG, log

from .dto import UrfuApiModel


class _Callback(Protocol):
    def __call__(self, model: UrfuApiModel, completed: bool):
        ...


class Retry(object):
    def __init__(
            self,
            exceptions: Optional[Any] = None,
            tries: Optional[int] = 5,
            delay: Optional[int] = 10,
            max_delay: Optional[int] = None,
            backoff: Optional[int] = 2,
            jitter: Optional[Union[tuple, int, None]] = (0, 2),
            off: Optional[bool] = False,
    ):
        """Returns a retry decorator.

        :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
        :param tries: the maximum number of attempts. default: -1 (infinite).
        :param delay: initial delay between attempts. default: 0.
        :param max_delay: the maximum value of delay. default: None (no limit).
        :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
        :param jitter: extra seconds added to delay between attempts. default: 0.
                       fixed if a number, random if a range tuple (min, max)
        :param off: Replace this decorator on empty if parameter is True
        :returns: a retry decorator.
        """
        self._exceptions = exceptions or Exception
        self._tries = tries
        self._delay = delay
        self._max_delay = max_delay
        self._backoff = backoff
        self._jitter = jitter
        self._off = off

    def __call__(self, func):
        if self._off is True:
            return func

        async def wrapped(*fargs, **fkwargs):
            args = fargs if fargs else list()
            kwargs = fkwargs if fkwargs else dict()
            return await self.__retry_internal(func, args, kwargs)

        return wrapped

    async def __retry_internal(self, func, args, kwargs):
        while self._tries:
            try:
                return await self.create_coroutine(func, args, kwargs)
            except self._exceptions as e:
                self._tries -= 1
                if not self._tries:
                    raise e

                log("%s, retrying in %s seconds...", e, self._delay)

                await asyncio.sleep(self._delay)

                self._delay *= self._backoff

                if isinstance(self._jitter, tuple):
                    self._delay += uniform(*self._jitter)
                else:
                    self._delay += self._jitter

                if self._max_delay is not None:
                    self._delay = min(self._delay, self._max_delay)

    @staticmethod
    def create_coroutine(func, args, kwargs):
        return func(*args, **kwargs)


class ApiClient:
    def __init__(self):
        self.callback: Optional[_Callback] = None

    def add_callback(self, fn: _Callback):
        self.callback = fn

    def __callbacks(self, model: UrfuApiModel, completed: bool):
        if self.callback:
            self.callback(model=model, completed=completed)

    @staticmethod
    @Retry(tries=20)
    async def get(page: int, size: int) -> UrfuApiModel:
        page = max(page, 1)
        size = max(size, 5)
        async with ClientSession() as session:
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }
            response = await session.get(
                f"https://urfu.ru/api/entrant/?page={page}&size={size}",
                headers=headers,
                raise_for_status=True,

            )
            log(f"ApiClient Получили ответ на загрузку информации page={page},size={size}")
            bytes_json = await response.read()
            return UrfuApiModel.model_validate_json(bytes_json)

    async def load_pages(self):
        model = await self.get(page=1, size=1)
        model.items = []
        pages = (model.count // 100) + 2
        for i in range(1, 3 if IS_DEBUG else pages):
            try:
                data = await self.get(page=i, size=100)
                model.items.extend(data.items)
            except Exception:
                import traceback
                traceback.print_exc()
            if (i % 3) == 0:
                self.__callbacks(model=model, completed=False)
                await asyncio.sleep(choice([0.3, 0.6, 1, 2, 4]))
        self.__callbacks(model=model, completed=True)


client = ApiClient()
