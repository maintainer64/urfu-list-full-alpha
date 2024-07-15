from typing import Protocol

import pandas as pd
from config import log

from .dto import UrfuApiShortModel
from .json_store import JsonStorage


class _Callback(Protocol):
    def __call__(self, loader: 'LoaderCSV'):
        ...


class LoaderCSV:
    def __init__(self):
        self.callback: _Callback | None = None
        self.reload()

    def add_reload_callback(self, fn):
        self.callback = fn

    def reload(self):
        log("LoaderCSV reload")
        self.LAST_UPDATED_MODEL = JsonStorage.load(UrfuApiShortModel)
        self.df = pd.read_csv('3.csv')
        self.LAST_UPDATED_DATE = self.LAST_UPDATED_MODEL.last_import
        self.ALL_COUNT = self.LAST_UPDATED_MODEL.count
        self.PAGE_SIZE = 500
        self.STATES_NAME = "Направление (специальность)"
        self.STATES = self.df[self.STATES_NAME].unique().tolist()
        self.STATES_LIST = [{"label": st, "value": st} for st in list(set(self.STATES))]
        self.SORTED_AUTO = [
            {'column_id': 'Вид конкурса', 'direction': 'asc'},
            {'column_id': 'Оригинал док. об образовании', 'direction': 'asc'},
            {'column_id': 'Сумма конкурсных баллов', 'direction': 'desc'},
            {'column_id': 'Приоритет', 'direction': 'asc'}
        ]
        self.callback(loader=self) if self.callback else None


loader_csv = LoaderCSV()
