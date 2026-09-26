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

    def _pick_language_version(self, config: Config | None = None) -> str | AccraError:
        """Picks a language version that works for the project and its dependencies."""

        cfg = config or self.spec.config

        supported_versions: set[str] | AccraError = (
            self._get_supported_language_versions_from_code(cfg)
        )
        match supported_versions:
            case set():
                pass
            case None:
                pass
            case AccraError():
                return supported_versions

        for manifest in self.present_manifests:
            result: set[str] | AccraError = manifest.get_supported_language_versions(
                cfg
            )
            match result:
                case set():
                    if not supported_versions:
                        supported_versions = result
                    else:
                        supported_versions = supported_versions.intersection(result)

                    if not supported_versions:
                        return AccraInstallError(
                            message="could not decide on a language version"
                        )

                case AccraError():
                    return result

        return next(iter(supported_versions))

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

    def _setup_environment(self, config: Config | None = None) -> AccraResult:
        """Anything that is needed to be done before the language and dependencies are installed (e.g. setting up venv for Python)."""
        return []

    @abstractmethod
    def install_language(
        self, language_version: str | None = None, config: Config | None = None
    ) -> AccraResult:
        """Installs the language toolchain."""
        return []

    @abstractmethod
    def install_dependency(
        self, dependency: DependencySpec, config: Config | None = None
    ) -> AccraResult:
        """Installs a dependency."""
        return []

    def build(self, config: Config | None = None) -> AccraResult:
        """Installs the language toolchain and the project's dependencies.

        See `setup_environment()` for work that needs to be done before anything is installed.
        """

        cfg = config or self.spec.config

        res: AccraResult = []
        dockerfile_instructions: list[DockerfileInstruction] = []

        language_version: str | None = self._pick_language_version(cfg)
        dependencies: set[DependencySpec] | None = self._get_dependencies(cfg)

        res = self._setup_environment(cfg)
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
