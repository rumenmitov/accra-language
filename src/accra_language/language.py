from abc import ABC, abstractmethod
from pydantic import BaseModel
from .environment_manager import EnvironmentManager
from .error import ErrorToken


class LanguageSpec(BaseModel):
    name: str
    version: str
    env_managers: list[EnvironmentManager] = Field(default_factory=set)
    analyzers: list[Analyzer] = Field(default_factory=set)


class Language(ABC):
    def __init__(self, spec: LanguageSpec):
        self.spec = spec

    @abstractmethod
    def detect_language(self) -> bool: ...

    @abstractmethod
    def install(self) -> ErrorToken | None: ...

    @abstractmethod
    def build(self) -> ErrorToken | None: ...

    @abstractmethod
    def run_program(self, program: str, args: [str]) -> ErrorToken | None: ...
