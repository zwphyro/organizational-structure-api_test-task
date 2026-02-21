from pydantic import BaseModel


class HTTPErrorSchema(BaseModel):
    detail: str

    class Config:
        json_schema_extra = {"example": {"detail": "Error message"}}
