from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from .config import Config
from .error import AccraError


class DependencySpec(BaseModel):
    # needed for so that DependencySpec can be used in sets
    model_config = ConfigDict(frozen=True)

    name: str
    version: str


class ManifestSpec(BaseModel):
    name: str
    version: str
    config: Config = Config()


class Manifest(ABC):
    def __init__(self, spec: ManifestSpec):
        self.spec = spec

    @abstractmethod
    def detect(self, config: Config | None = None) -> bool:
        """Returns True if the manifest is present in the project, False otherwise."""
        return False

    @abstractmethod
    def extract_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None:
        """Returns all dependencies listed in the manifest."""
        return None

    @abstractmethod
    def get_supported_language_versions(
        self, config: Config | None = None
    ) -> set[str] | AccraError:
        """Returns all language versions that are allowed by the manifest."""
        return None
