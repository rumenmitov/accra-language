from pathlib import Path

from test_environment_manager import ConfigurableEnvironmentManager, FakeManifest

from accra_language import (
    AccraError,
    Config,
    EnvironmentManagerSpec,
    Language,
    LanguageSpec,
    multilingual_plugin_error,
)
from accra_language.language import _version_key


class _StaticLanguage(Language):
    def extract_static_facts(self):
        return set()


def _bare_language():
    config = Config()
    manager = ConfigurableEnvironmentManager(config)
    return _StaticLanguage(
        LanguageSpec(
            name="bare",
            version="1",
            config=config,
            supported_env_managers={manager},
        ),
        manager,
    ), manager


def test_unsupported_defaults_are_unsupported_and_accra_errors():
    language, _ = _bare_language()
    results = [
        language.check_script(Path("x")),
        language.read_script(""),
    ]
    for result in results:
        assert isinstance(result, multilingual_plugin_error)
        assert isinstance(result, AccraError)


def test_manager_with_manifests_is_preferred():
    config = Config()
    manifest = FakeManifest(config)
    with_manifest = ConfigurableEnvironmentManager(
        config, manifests=[manifest], name="zeta"
    )
    without = ConfigurableEnvironmentManager(config, name="alpha")
    language = _StaticLanguage(
        LanguageSpec(
            name="",
            version="",
            config=config,
            supported_env_managers={with_manifest, without},
        )
    )
    language.detect()
    assert language.env_manager is with_manifest


def test_versions_compare_numerically():
    config = Config()
    managers = []
    for version in ("10.0", "9.0", "2.1"):
        manager = ConfigurableEnvironmentManager(config, name="same")
        manager.spec = EnvironmentManagerSpec(
            name="same", version=version, supported_manifests=set(), config=config
        )
        managers.append(manager)
    language = _StaticLanguage(
        LanguageSpec(
            name="", version="", config=config, supported_env_managers=set(managers)
        )
    )
    language.build()
    assert language.env_manager.spec.version == "2.1"
    assert _version_key("10") > _version_key("9")
    assert _version_key("1.0a") != _version_key("1.0")  # text part does not raise
