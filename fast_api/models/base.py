from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BaseDocument(BaseModel):
    """Base class for Elasticsearch models."""
    uuid: str = Field(alias='uuid', default=None)

    @field_validator('uuid', mode='before')
    @classmethod
    def transform_uuid(cls, raw_id: UUID | str) -> str:
        return str(raw_id)
