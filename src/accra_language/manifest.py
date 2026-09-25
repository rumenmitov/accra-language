from abc import ABC, abstractmethod

from pydantic import BaseModel

from .config import Config
from .dockerfile import DockerfileInstruction


class DependencySpec(BaseModel):
    name: str
    version: str
    instructions: list[DockerfileInstruction]


class ManifestSpec(BaseModel):
    name: str
    version: str
    config: Config


class Manifest(ABC):
    def __init__(self, spec: ManifestSpec):
        self.spec = spec

    @abstractmethod
    def detect(self, config: Config | None = None) -> bool: ...

    @abstractmethod
    def extract_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None: ...
