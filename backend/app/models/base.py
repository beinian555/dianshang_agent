from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    pass


class PydanticJSONB(TypeDecorator):
    """Store Pydantic models as JSONB. Supports both single models and lists."""
    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_type=None, is_list: bool = False):
        super().__init__()
        self.pydantic_type = pydantic_type
        self.is_list = is_list

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if self.is_list:
            return [
                item if isinstance(item, dict) else item.model_dump(mode="json")
                for item in value
            ]
        if isinstance(value, dict):
            return value
        return value.model_dump(mode="json")

    def process_result_value(self, value, dialect):
        if value is None or self.pydantic_type is None:
            return value
        if self.is_list:
            return [self.pydantic_type(**item) for item in value]
        return self.pydantic_type(**value)

    def copy(self, **kw):
        return PydanticJSONB(
            pydantic_type=self.pydantic_type,
            is_list=self.is_list,
        )
