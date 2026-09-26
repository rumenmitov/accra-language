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
    def __init__(self):
        spec = ManifestSpec(name="fake-manifest", version="1.0.0")
        super().__init__(spec)

    @override
    def detect(self, config: Config | None = None) -> bool:
        return True

    @override
    def extract_dependencies(
        self, config: Config | None = None
    ) -> set[DependencySpec] | None:
        return {DependencySpec(name="foo", version="4.5")}

    @override
    def get_supported_language_versions(
        self, config: Config | None = None
    ) -> set[str] | AccraError:
        return {"1.0"}


class FakeEnvironmentManager(EnvironmentManager):
    def __init__(self):
        manifest = FakeManifest()
        spec = EnvironmentManagerSpec(
            name="fake-env-manager", version="1.0.0", supported_manifests={manifest}
        )

        super().__init__(spec)

    @override
    def install_language(
        self, language_version: str | None = None, config: Config | None = None
    ) -> AccraResult:
        return [DockerfileInstruction('RUN echo "Test language installed!"')]

    @override
    def install_dependency(
        self, dependency: DependencySpec, config: Config | None = None
    ) -> AccraResult:
        return [
            DockerfileInstruction(
                f'RUN echo "Dependency {dependency.name}-{dependency.version} installed!"'
            )
        ]


def test_build_environment():
    env_mgr = FakeEnvironmentManager()
    dockerfile: list[DockerfileInstruction] = env_mgr.build()

    correct_dockerfile: list[DockerfileInstruction] = [
        'RUN echo "Test language installed!"',
        'RUN echo "Dependency foo-4.5 installed!"',
    ]

    assert dockerfile == correct_dockerfile
