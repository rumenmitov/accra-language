from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class DependencySpec(BaseModel):
    name: str
    version: str


class ManifestSpec(BaseModel):
    name: str
    version: str


class Manifest(ABC):
    def __init__(self, spec: ManifestSpec):
        self.spec = spec

    @abstractmethod
    def detect_manifest(self) -> bool: ...

    @abstractmethod
    def extract_dependencies(self) -> set[DependencySpec] | None: ...
