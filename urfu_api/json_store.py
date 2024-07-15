from typing import TypeVar

from pydantic import BaseModel

_SCHEMA = TypeVar("_SCHEMA", bound=BaseModel)


class JsonStorage:
    @staticmethod
    def save(model: _SCHEMA):
        json_name = f"{model.__class__.__name__}.json"
        with open(json_name, "w") as fin:
            fin.write(model.model_dump_json(indent=2))

    @staticmethod
    def load(model_name: type[_SCHEMA]) -> _SCHEMA:
        json_name = f"{model_name.__name__}.json"
        with open(json_name, "r") as fin:
            return model_name.model_validate_json(fin.read())
