from abc import ABC

from pydantic import BaseModel


class AccraError(ABC, BaseModel):
    message: str
