from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    def __repr__(self):
        params = {x: self.__getattribute__(x) for x in self.__dict__ if not x.startswith('_')}
        return self.__class__.__name__ + "(" + ", ".join(f"{key}={value}" for key, value in params.items()) + ")"
