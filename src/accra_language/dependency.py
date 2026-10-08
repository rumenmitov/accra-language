from pydantic import BaseModel, ConfigDict


class Dependency(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    version: str
