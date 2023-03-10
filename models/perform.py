from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List


class Perform(BaseModel):
    id: str = Field(None, alias="_id")
    patientId: str
    therapistId: str
    therapistName: str
    exerciseType: str
    exerciseName: str
    repetitionCount: int

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data