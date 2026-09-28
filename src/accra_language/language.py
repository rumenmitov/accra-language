from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, InstanceOf

from .analyzer import Analyzer
from .config import Config
from .dockerfile import DockerfileInstruction
from .environment_manager import EnvironmentManager
from .error import AccraError
from .result import AccraResult


class LanguageSpec(BaseModel):
    name: str
    version: str
    config: Config = Config()
    supported_env_managers: set[InstanceOf[EnvironmentManager]] = Field(
        default_factory=set
    )
    analyzers: set[InstanceOf[Analyzer]] = Field(default_factory=set)


class Language(ABC):
    def __init__(
        self, spec: LanguageSpec, env_manager: EnvironmentManager | None = None
    ):
        self.spec = spec
        self.env_manager: EnvironmentManager | None = env_manager or next(
            iter(spec.supported_env_managers)
        )

    @abstractmethod
    def detect(self, config: Config | None = None) -> bool:
        """Detects if the language is present in this project."""
        ...

    def build(self, config: Config | None = None) -> AccraResult:
        """Builds the project and determines the Dockerfile instructions."""

        if not self.env_manager:
            return []

        cfg = config or self.spec.config

        dockerfile: list[DockerfileInstruction] = []

        setup_result: AccraResult = self.env_manager.setup(cfg)
        match setup_result:
            case list():
                dockerfile.extend(setup_result)
            case AccraError():
                return setup_result

        installation_result: AccraResult = self.env_manager.install_dependencies(cfg)
        match installation_result:
            case list():
                dockerfile.extend(installation_result)
            case AccraError():
                return installation_result

        build_result: AccraResult = self.env_manager.build(cfg)
        match build_result:
            case list():
                dockerfile.extend(build_result)
            case AccraError():
                return build_result
