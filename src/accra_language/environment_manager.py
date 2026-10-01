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
    config: Config
    supported_manifests: set[InstanceOf[Manifest]] = Field(default_factory=set)


class EnvironmentManager(ABC):
    def __init__(self, spec: EnvironmentManagerSpec):
        self.spec = spec
        self.present_manifests: set[Manifest] = {
            manifest for manifest in spec.supported_manifests if manifest.detect()
        }

    def _get_dependencies(self) -> set[DependencySpec] | None:
        """Collects the dependencies from all present manifests into a single set."""

        dependencies: set[DependencySpec] = set()

        for manifest in self.present_manifests:
            manifest_dependencies: set[DependencySpec] | None = (
                manifest.extract_dependencies()
            )
            if manifest_dependencies:
                dependencies.update(manifest_dependencies)

        if not dependencies:
            return None

        return dependencies

    def _get_supported_language_versions_from_code(
        self,
    ) -> set[str] | AccraError | None:
        """Returns all the language versions that the project code can run on."""
        return None

    @abstractmethod
    def setup(self) -> AccraResult:
        """Installation of the language toolchain (e.g. language compiler / interpreter, package manager) and setup of the environment (e.g. venv for Python)."""
        return []

    @abstractmethod
    def _install_dependency(self, dependency: DependencySpec) -> AccraResult:
        """Installs a dependency."""
        return []

    def select_language_version(self) -> str | AccraError:
        """Selects a language version that works for the project and its dependencies."""

        supported_versions: set[str] | AccraError | None = (
            self._get_supported_language_versions_from_code()
        )

        if isinstance(supported_versions, AccraError):
            return supported_versions

        if not supported_versions:
            supported_versions = {self.spec.default_language_version}

        for manifest in self.present_manifests:
            result: set[str] | AccraError = manifest.get_supported_language_versions()
            match result:
                case set():
                    if result:
                        supported_versions = supported_versions.intersection(result)

                    if not supported_versions:
                        return AccraInstallError(
                            message="could not decide on a language version"
                        )

                case AccraError():
                    return result

        return next(iter(supported_versions))

    def install_dependencies(self) -> AccraResult:
        """Installs all project dependencies."""

        res: AccraResult = []
        dockerfile_instructions: list[DockerfileInstruction] = []

        dependencies: set[DependencySpec] | None = self._get_dependencies()

        if not dependencies:
            return []

        for dependency in dependencies:
            res = self._install_dependency(dependency)
            match res:
                case AccraError():
                    return res

                case list():
                    dockerfile_instructions.extend(res)

        return sorted(dockerfile_instructions)

    def build(self) -> AccraResult:
        """Build / compile the project."""
        return []
