from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from .config import Config
from .error import AccraInstallError
from .manifest import DependencySpec, Manifest


class EnvironmentManagerSpec(BaseModel):
    name: str
    version: str
    config: Config
    manifests: set[Manifest] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec

    @abstractmethod
    def install(self, config: Config | None = None) -> AccraInstallError | None: ...

    @abstractmethod
    def install_dependencies(
        self, dependencies: set[DependencySpec], config: Config | None = None
    ) -> AccraInstallError | None: ...
