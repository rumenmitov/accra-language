from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field

from .analyzer import Analyzer
from .environment_manager import EnvironmentManager
from .error import AccraBuildError, AccraInstallError, AccraRunError


class LanguageSpec(BaseModel):
    name: str
    version: str
    env_managers: set[EnvironmentManager] = Field(default_factory=set)
    analyzers: set[Analyzer] = Field(default_factory=set)


class Language(ABC):
    def __init__(self, spec: LanguageSpec):
        self.spec = spec

    @abstractmethod
    def detect_language(self, root: Path) -> bool: ...

    @abstractmethod
    def install(self) -> AccraInstallError | None: ...

    @abstractmethod
    def build(self) -> AccraBuildError | None: ...

    @abstractmethod
    def run_program(self, program: str, args: [str]) -> AccraRunError | None: ...
