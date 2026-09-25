from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from .analyzer import Analyzer
from .config import Config
from .environment_manager import EnvironmentManager
from .result import AccraResult


class LanguageSpec(BaseModel):
    name: str
    version: str
    config: Config
    supported_env_managers: set[EnvironmentManager] = Field(default_factory=set)
    analyzers: set[Analyzer] = Field(default_factory=set)


class Language(ABC):
    def __init__(
        self, spec: LanguageSpec, env_manager: EnvironmentManager | None = None
    ):
        self.spec = spec
        self.env_manager = env_manager or next(iter(spec.supported_env_managers))

    @abstractmethod
    def detect_language(self, config: Config | None = None) -> bool:
        """Detects if the language is present in this project."""
        ...

    def build(self, config: Config | None = None) -> AccraResult:
        """Builds the project and determines the Dockerfile instructions."""

        cfg = config or self.spec.config

        return self.env_manager.build(cfg)
