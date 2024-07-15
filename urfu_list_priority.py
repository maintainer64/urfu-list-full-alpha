import asyncio
from datetime import datetime

from urfu_api.api_client import client
from urfu_api.json_store import JsonStorage
from urfu_api.dto import UrfuApiShortModel, UrfuApiModel
from urfu_api.csv_loader import loader_csv
from urfu_api.csv_creator_use_case import CsvCreatorUseCase
from config import log


def callback_loader_api(model: UrfuApiModel, completed: bool):
    JsonStorage.save(model=model)
    if completed:
        JsonStorage.save(model=UrfuApiShortModel(
            last_import=model.last_import,
            count=model.count,
        ))
        uc = CsvCreatorUseCase()
        uc.execute(model=model)


async def job_async():
    last_upd = JsonStorage.load(UrfuApiShortModel)
    log(f"Загрузил данные с локали по датам date_load={last_upd.last_import} count_load={last_upd.count}")
    model_info = await client.get(page=1, size=1)
    log(last_upd.last_import, model_info.last_import)
    interval = abs(datetime.now() - model_info.last_import)
    if interval.total_seconds() // 60 <= 7:
        log("Urfu сейчас обновляется, надо подождать")
        return
    if last_upd.last_import >= model_info.last_import:
        log("В сервисе хранятся последние обновленные данные")
        return
    log("Обновляю данные локально")
    client.add_callback(fn=callback_loader_api)
    await client.load_pages()
    log("Перезагружаю приложение")
    loader_csv.reload()


def job():
    log("JOB IS ALIVE")
    asyncio.run(job_async())
