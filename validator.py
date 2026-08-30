from pydantic import BaseModel

class DataValidator:
    def __init__(self, schema: BaseModel):
        self.schema = schema

    def validate(self, data: dict) -> tuple:
        pass
