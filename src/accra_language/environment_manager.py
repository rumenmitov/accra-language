from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from .error import AccraLanguageError
from .manifest import Manifest, DependencySpec


class EnvironmentManagerSpec(BaseModel):
    name: str
    version: str
    manifests: set[Manifest] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec

    @abstractmethod
    def install(self) -> AccraLanguageError | None: ...

    @abstractmethod
    def install_dependencies(
        self, dependency: set[DependencySpec]
    ) -> AccraLanguageError | None: ...
