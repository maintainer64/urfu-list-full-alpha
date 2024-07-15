from datetime import datetime
from pydantic import BaseModel


class UrfuApplicationMarkItem(BaseModel):
    mark: int = 0
    case: str = ""


class UrfuApplicationItem(BaseModel):
    status: str = ""
    competition: str = ""
    edu_doc_original: bool = False
    priority: int = -1
    speciality: str = ""
    program: str = ""
    familirization: str = ""
    compensation: str = ""
    achievs: int = 0
    total_mark: int = 0
    marks: dict[str, UrfuApplicationMarkItem] = dict()


class UrfuRow(BaseModel):
    applications: list[UrfuApplicationItem] = []
    regnum: int = 0
    snils: str = ""


class UrfuApiModel(BaseModel):
    last_import: datetime
    count: int
    page: int = 0
    size: int = 0
    items: list[UrfuRow] = []


class UrfuApiShortModel(BaseModel):
    last_import: datetime
    count: int
