from typing import override

from accra_language import (
    AccraError,
    AccraResult,
    Config,
    DependencySpec,
    DockerfileInstruction,
    EnvironmentManager,
    EnvironmentManagerSpec,
    Manifest,
    ManifestSpec,
)


class FakeManifest(Manifest):
    def __init__(self, config: Config):
        spec = ManifestSpec(name="fake-manifest", version="1.0.0", config=config)
        super().__init__(spec)

    @override
    def detect(self) -> bool:
        return True

    @override
    def extract_dependencies(self) -> set[DependencySpec] | None:
        return {DependencySpec(name="foo", version="4.5")}

    @override
    def get_supported_language_versions(self) -> set[str] | AccraError:
        return {"9.0"}


class FakeEnvironmentManager(EnvironmentManager):
    def __init__(self, config: Config):
        manifest = FakeManifest(config)
        spec = EnvironmentManagerSpec(
            name="fake-env-manager",
            version="1.0.0",
            default_language_version="9.0",
            supported_manifests={manifest},
            config=config,
        )

        super().__init__(spec)

    @override
    def setup(self) -> AccraResult:
        language_ver_result: str | AccraError = self.select_language_version()
        if isinstance(language_ver_result, AccraError):
            return language_ver_result

        return [
            DockerfileInstruction(
                f'RUN echo "Fake language, version {language_ver_result}, installed!"'
            ),
            DockerfileInstruction(
                'RUN echo "Fake environment manager setup complete!"'
            ),
        ]

    @override
    def _install_dependency(self, dependency: DependencySpec) -> AccraResult:
        return [
            DockerfileInstruction(
                f'RUN echo "Dependency {dependency.name}-{dependency.version} installed!"'
            )
        ]

    @override
    def build(self) -> AccraResult:
        return [DockerfileInstruction('RUN echo "Build complete!"')]


def test_environment_manager():
    dockerfile: list[DockerfileInstruction] = []
    correct_dockerfile: list[DockerfileInstruction] = [
        'RUN echo "Fake language, version 9.0, installed!"',
        'RUN echo "Fake environment manager setup complete!"',
        'RUN echo "Dependency foo-4.5 installed!"',
        'RUN echo "Build complete!"',
    ]

    config = Config()

    env_mgr = FakeEnvironmentManager(config)
    result: AccraResult = env_mgr.setup()

    assert not isinstance(result, AccraError)
    dockerfile.extend(result)

    result = env_mgr.install_dependencies()

    assert not isinstance(result, AccraError)
    dockerfile.extend(result)

    result = env_mgr.build()

    assert not isinstance(result, AccraError)
    dockerfile.extend(result)

    assert dockerfile == correct_dockerfile
