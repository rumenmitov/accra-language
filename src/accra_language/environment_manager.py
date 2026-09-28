from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, InstanceOf

from .config import Config
from .dockerfile import DockerfileInstruction
from .error import AccraError, AccraInstallError
from .manifest import DependencySpec, Manifest
from .result import AccraResult


class EnvironmentManagerSpec(BaseModel):
    name: str
    version: str
    default_language_version: str
    config: Config = Config()
    supported_manifests: set[InstanceOf[Manifest]] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec
        self.present_manifests: set[Manifest] = {
            manifest
            for manifest in spec.supported_manifests
            if manifest.detect(spec.config)
        }

    def _get_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None:
        """Collects the dependencies from all present manifests into a single set."""

        cfg = config or self.spec.config
        dependencies: set[DependencySpec] = set()

        for manifest in self.present_manifests:
            manifest_dependencies: set[DependencySpec] | None = (
                manifest.extract_dependencies(cfg)
            )
            if manifest_dependencies:
                dependencies.update(manifest_dependencies)

        if not dependencies:
            return None

        return dependencies

    def _get_supported_language_versions_from_code(
        self, config: Config | None = None
    ) -> set[str] | AccraError | None:
        """Returns all the language versions that the project code can run on."""
        return None

    @abstractmethod
    def setup(self, config: Config | None = None) -> AccraResult:
        """Installation of the language toolchain (e.g. language compiler / interpreter, package manager) and setup of the environment (e.g. venv for Python)."""
        return []

    @abstractmethod
    def _install_dependency(
        self, dependency: DependencySpec, config: Config | None = None
    ) -> AccraResult:
        """Installs a dependency."""
        return []

    def select_language_version(self, config: Config | None = None) -> str | AccraError:
        """Selects a language version that works for the project and its dependencies."""

        cfg = config or self.spec.config

        supported_versions: set[str] | AccraError | None = (
            self._get_supported_language_versions_from_code(cfg)
        )
        match supported_versions:
            case set() | None:
                supported_versions = {self.spec.default_language_version}
            case AccraError():
                return supported_versions

        for manifest in self.present_manifests:
            result: set[str] | AccraError = manifest.get_supported_language_versions(
                cfg
            )
            match result:
                case set():
                    supported_versions = supported_versions.intersection(result)

                    if not supported_versions:
                        return AccraInstallError(
                            message="could not decide on a language version"
                        )

                case AccraError():
                    return result

        return next(iter(supported_versions))

    def install_dependencies(self, config: Config | None = None) -> AccraResult:
        """Installs all project dependencies."""

        cfg = config or self.spec.config

        res: AccraResult = []
        dockerfile_instructions: list[DockerfileInstruction] = []

        dependencies: set[DependencySpec] | None = self._get_dependencies(cfg)

        if not dependencies:
            return []

        for dependency in dependencies:
            res = self._install_dependency(dependency)
            match res:
                case AccraError():
                    return res

                case list():
                    dockerfile_instructions.extend(res)

        return dockerfile_instructions

    def build(self, config: Config | None = None) -> AccraResult:
        """Build / compile the project."""
        return []
