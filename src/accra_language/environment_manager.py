from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from .error import AccraInstallError
from .manifest import DependencySpec, Manifest


class EnvironmentManagerSpec(BaseModel):
    name: str
    version: str
    manifests: set[Manifest] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec

    @abstractmethod
    def install(self) -> AccraInstallError | None: ...

    @abstractmethod
    def install_dependencies(
        self, dependency: set[DependencySpec]
    ) -> AccraInstallError | None: ...
