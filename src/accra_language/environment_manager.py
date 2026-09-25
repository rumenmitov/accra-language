from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from .config import Config
from .dockerfile import DockerfileInstruction
from .error import AccraError
from .manifest import DependencySpec, Manifest
from .result import AccraResult


class EnvironmentManagerSpec(BaseModel):
    name: str
    version: str
    config: Config
    manifests: set[Manifest] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec

    def _pick_language_version(self, config: Config | None = None) -> str | None:
        """Picks a language version that works for the project and its dependencies."""

        cfg = config or self.spec.config

        supported_versions_per_manifest: list[set[str]] = set()
        supported_versions: set[str] | None = None
        language_version: str | None = None

        for manifest in self.spec.manifests:
            supported_versions_per_manifest.append(
                manifest.get_supported_language_versions(cfg)
            )

        supported_versions = set.intersection(*supported_versions_per_manifest) or None
        if supported_versions:
            language_version = next(iter(supported_versions))

        return language_version

    def _get_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None:
        """Collects the dependencies from all present manifests into a single set."""

        cfg = config or self.spec.config
        dependencies: set[DependencySpec] = set()

        for manifest in self.spec.manifests:
            manifest_dependencies: set[DependencySpec] | None = (
                manifest.extract_dependencies(cfg)
            )
            if manifest_dependencies:
                dependencies.update(manifest_dependencies)

        if not dependencies:
            return None

        return dependencies

    @abstractmethod
    def setup_environment(self, config: Config | None = None) -> AccraResult:
        """Anything that is needed to be done before the language and dependencies are installed (e.g. setting up venv for Python)."""
        ...

    @abstractmethod
    def install_language(
        self, language_version: str | None = None, config: Config | None = None
    ) -> AccraResult:
        """Installs the language toolchain."""
        ...

    @abstractmethod
    def install_dependency(
        self, dependency: DependencySpec, config: Config | None = None
    ) -> AccraResult:
        """Installs a dependency."""
        ...

    def build_environment(self, config: Config | None = None) -> AccraResult:
        """Installs the language toolchain and the project's dependencies.

        See `setup_environment()` for work that needs to be done before anything is installed.
        """

        cfg = config or self.spec.config

        res: AccraResult = []
        dockerfile_instructions: list[DockerfileInstruction] = []

        language_version: str | None = self._pick_language_version(cfg)
        dependencies: set[DependencySpec] | None = self._get_dependencies(cfg)

        res = self.setup_environment(cfg)
        match res:
            case AccraError():
                return res
            case list():
                dockerfile_instructions.extend(res)

        res = self.install_language(language_version, cfg)
        match res:
            case AccraError():
                return res
            case list():
                dockerfile_instructions.extend(res)

        for dependency in dependencies:
            res = self.install_dependency(dependency, cfg)
            match res:
                case AccraError():
                    # TODO How should we handle the individual
                    # installation errors? Perhaps we query the LLM?
                    pass
                case list():
                    dockerfile_instructions.extend(res)

        return dockerfile_instructions
