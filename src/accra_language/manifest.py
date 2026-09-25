from abc import ABC, abstractmethod

from pydantic import BaseModel

from .config import Config
from .dockerfile import DockerfileInstruction
from .error import AccraError


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
    def detect(self, config: Config | None = None) -> bool:
        """Returns True if the manifest is present in the project, False otherwise."""
        ...

    @abstractmethod
    def extract_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None:
        """Returns all dependencies listed in the manifest."""
        ...

    @abstractmethod
    def get_supported_language_versions(
        self, config: Config | None = None
    ) -> set[str] | AccraError:
        """Returns all language versions that are allowed by the manifest."""
        ...
