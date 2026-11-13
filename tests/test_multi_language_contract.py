"""The contract parts a caller needs for any language: read-only presence, the
toolchain and analysis. All are optional for a plugin and have defaults."""

from pathlib import Path
from typing import override

from accra_language import (
    AccraError,
    AccraResult,
    AnalysisRun,
    Analyzer,
    AnalyzerSpec,
    Config,
    Dependency,
    Dockerfile,
    EntryPoint,
    EnvironmentManager,
    EnvironmentManagerSpec,
    Language,
    LanguageSpec,
    Manifest,
    ManifestSpec,
    MemoryProfile,
    Metrics,
    Toolchain,
)


class FileManifest(Manifest):
    """Present when its file exists in `cwd`."""

    def __init__(self, config: Config, filename: str):
        super().__init__(ManifestSpec(name=filename, version="", config=config))

    @override
    def detect(self) -> bool:
        return (Path(self.spec.config.cwd) / self.spec.name).is_file()

    @override
    def extract_dependencies(self) -> set[Dependency]:
        return set()

    @override
    def get_supported_language_versions(self) -> set[str] | AccraError:
        return {"1"}


class PlainEnvironmentManager(EnvironmentManager):
    """Implements only what the contract requires."""

    def __init__(self, config: Config, manifests=()):
        super().__init__(
            EnvironmentManagerSpec(
                name="plain",
                version="",
                config=config,
                supported_manifests=set(manifests),
            )
        )

    @override
    def pre_dependencies_installation(self) -> AccraResult:
        return AccraResult()

    @override
    def _install_dependency(self, dependency: Dependency) -> AccraResult:
        return AccraResult()


def _language(config, env_managers=(), toolchain=None):
    spec = LanguageSpec(
        name="toy",
        version="1",
        config=config,
        supported_env_managers=set(env_managers),
        toolchain=toolchain or Toolchain(),
    )
    return Language(spec)


def test_entry_point_and_toolchain_are_frozen_models():
    entry = EntryPoint(name="tool", kind="binary", command=("./tool",))
    assert {entry, EntryPoint(name="tool", kind="binary", command=("./tool",))} == {
        entry
    }
    toolchain = Toolchain(executables=("cargo",), packages=("build-essential",))
    assert hash(toolchain) == hash(
        Toolchain(executables=("cargo",), packages=("build-essential",))
    )


def test_toolchain_installs_for_a_home(tmp_path):
    toolchain = Toolchain(
        executables=("toy",),
        install=("git clone https://example.org/toy {home}/.toy",),
        environment=(("TOY_ROOT", "{home}/.toy"),),
        path=("{home}/.toy/bin", "/usr/bin"),
    )
    assert hash(toolchain) == hash(toolchain.model_copy())
    rendered = toolchain.for_home(tmp_path)
    assert rendered.install == (f"git clone https://example.org/toy {tmp_path}/.toy",)
    assert rendered.environment == (("TOY_ROOT", f"{tmp_path}/.toy"),)
    env = rendered.applied_to({"PATH": "/usr/bin:/bin", "KEEP": "1"})
    assert env == {
        "PATH": f"{tmp_path}/.toy/bin:/usr/bin:/bin",
        "KEEP": "1",
        "TOY_ROOT": f"{tmp_path}/.toy",
    }
    assert rendered.applied_to(env) == env
    assert Toolchain().applied_to({"PATH": "/bin"}) == {"PATH": "/bin"}
    assert Toolchain().install == () and Toolchain().environment == ()


def test_presence_is_read_only_and_manifest_based(tmp_path):
    config = Config(cwd=tmp_path)
    language = _language(
        config, [PlainEnvironmentManager(config, [FileManifest(config, "toy.toml")])]
    )
    assert language.is_present() is False

    (tmp_path / "toy.toml").write_text("")
    config = Config(cwd=tmp_path)
    language = _language(
        config, [PlainEnvironmentManager(config, [FileManifest(config, "toy.toml")])]
    )
    assert language.is_present() is True
    assert language.env_manager is None  # nothing was selected or built
    assert sorted(p.name for p in tmp_path.iterdir()) == ["toy.toml"]


def test_missing_tools_uses_the_config_path(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    tool = bin_dir / "toytool"
    tool.write_text("#!/bin/sh\n")
    tool.chmod(0o755)
    config = Config(cwd=tmp_path, env={"PATH": str(bin_dir)})
    language = _language(
        config, toolchain=Toolchain(executables=("toytool", "no-such-tool-accra"))
    )

    assert language.missing_tools() == ("no-such-tool-accra",)


class FakeAnalyzer(Analyzer):
    """Measures each run it is given with `profiles`."""

    def __init__(self, config, name, metric, profiles=None):
        super().__init__(AnalyzerSpec(name=name, config=config, metrics={metric}))
        self.profiles = profiles if profiles is not None else set()
        self.calls = []

    @override
    def analyze_project(self, env_manager, runs=()):
        self.calls.append(([run.entry_point.name for run in runs], env_manager))
        return {run.entry_point: self.profiles for run in runs}


def test_analyze_project_runs_the_matching_analyzers_on_the_runs(tmp_path):
    config = Config(cwd=tmp_path)
    memory = FakeAnalyzer(
        config,
        "mem",
        Metrics.MEMORY,
        profiles={
            MemoryProfile(duration_ms=5, peak_memory_mb=1.0, total_memory_mb=2.0)
        },
    )
    broken = FakeAnalyzer(
        config,
        "net",
        Metrics.NETWORK,
        profiles=AccraError(error="net failed"),
    )
    spec = LanguageSpec(
        name="toy",
        version="1",
        config=config,
        supported_env_managers={PlainEnvironmentManager(config)},
        analyzers={memory, broken},
    )
    language = Language(spec)
    entry = EntryPoint(name="main", kind="script", command=("toy", "main"))
    run = AnalysisRun(
        entry_point=entry,
        args=("--n", "3"),
        env={"A": "1"},
        timeout=5,
        output_dir=tmp_path,
    )

    results = language.analyze_project(runs=[run])

    assert list(results) == ["mem", "net"]  # name order
    assert results["mem"] == {entry: memory.profiles}
    assert isinstance(results["net"][entry], AccraError)
    assert memory.calls[0][0] == ["main"] and memory.calls[0][1].spec.name == "plain"

    # the run's arguments, environment, timeout and report directory reach the analyzer
    assert run.args == ("--n", "3") and run.env == {"A": "1"}
    assert run.timeout == 5 and run.output_dir == tmp_path

    only_memory = language.analyze_project({Metrics.MEMORY}, [run])
    assert list(only_memory) == ["mem"]

    # no env manager: the error stands for the whole project
    no_manager = Language(
        LanguageSpec(name="toy", version="1", config=config, analyzers={memory})
    )
    assert isinstance(no_manager.analyze_project(runs=[run])["mem"][None], AccraError)


def test_profiles_carry_exit_code_and_report():
    profile = MemoryProfile(duration_ms=1, peak_memory_mb=1.0, total_memory_mb=1.0)
    assert profile.exit_code is None and profile.report is None
    failing = MemoryProfile(
        duration_ms=1, peak_memory_mb=1.0, total_memory_mb=1.0, exit_code=2, report="r"
    )
    assert failing.exit_code == 2 and failing.report == "r"


def test_dockerfile_parts_compose(tmp_path):
    first = Dockerfile(
        pre_dependencies_installation=["RUN install-python", "RUN uv venv"],
        dependencies_installation=["RUN uv pip install six"],
    )
    second = Dockerfile(
        pre_dependencies_installation=["RUN install-rust"],
        post_dependencies_installation=["RUN cargo build"],
    )
    first.extend(second)

    assert first.project_steps() == [
        "RUN install-python",
        "RUN uv venv",
        "RUN install-rust",
        "RUN uv pip install six",
        "RUN cargo build",
    ]
    assert str(Dockerfile(pre_dependencies_installation=["RUN x"])).startswith("RUN x")


def test_manifest_paths(tmp_path):
    (tmp_path / "toy.toml").write_text("")
    config = Config(cwd=tmp_path)
    manager = PlainEnvironmentManager(
        config, [FileManifest(config, "toy.toml"), FileManifest(config, "absent.toml")]
    )
    language = _language(config, [manager])

    assert language.manifest_paths() == {tmp_path / "toy.toml"}


def test_supported_versions_are_available_without_choosing(tmp_path):
    (tmp_path / "toy.toml").write_text("")
    config = Config(cwd=tmp_path)
    manager = PlainEnvironmentManager(config, [FileManifest(config, "toy.toml")])

    assert manager.supported_language_versions() == {"1"}
    assert manager.selected_language_version is None
    assert manager.select_language_version() == "1"
    assert isinstance(
        PlainEnvironmentManager(config).supported_language_versions(), AccraError
    )


def test_usage_scripts_are_unsupported_by_default(tmp_path):
    from accra_language import ScriptProfile

    config = Config(cwd=tmp_path)
    language = _language(config, [PlainEnvironmentManager(config)])
    assert language.script_profile() is None
    assert isinstance(language.check_script(tmp_path / "s.toy"), AccraError)
    assert isinstance(language.read_script("x"), AccraError)

    profile = ScriptProfile(language="Toy", file_suffix=".toy", code_fence="toy")
    assert profile.conventions == ()
    # What describes running the language's programs defaults to none
    assert (profile.run_command, profile.cli_frameworks, profile.project_files) == (
        "",
        (),
        (),
    )


def test_static_analyzers_need_no_runs(tmp_path):
    # static analyses of the sources (network, parallelism)
    from accra_language import (
        FileModules,
        NetworkProfile,
        ParallelismProfile,
        ParallelismUsage,
    )

    class Static(Analyzer):
        def __init__(self, config, name, metric, result):
            super().__init__(AnalyzerSpec(name=name, config=config, metrics={metric}))
            self.result = result
            self.seen = []

        @override
        def analyze_project(self, env_manager, runs=()):
            self.seen.append(env_manager.spec.name)
            return {None: self.result}

    config = Config(cwd=tmp_path)
    network = Static(
        config,
        "net",
        Metrics.NETWORK,
        {NetworkProfile(duration_ms=1, requires_network=True)},
    )
    threads = Static(
        config,
        "par",
        Metrics.PARALLELISM,
        {
            ParallelismProfile(
                duration_ms=1,
                multithreading=ParallelismUsage(
                    used=True,
                    modules=("threading",),
                    files=(FileModules(path="a.py", modules=("threading",)),),
                ),
            )
        },
    )
    broken = Static(config, "zzz", Metrics.NETWORK, AccraError(error="unreadable"))
    spec = LanguageSpec(
        name="toy",
        version="1",
        config=config,
        supported_env_managers={PlainEnvironmentManager(config)},
        analyzers={network, threads, broken},
    )
    language = Language(spec)

    results = language.analyze_project()
    assert list(results) == ["net", "par", "zzz"]
    assert results["net"] == {None: network.result} and network.seen == ["plain"]
    [profile] = results["par"][None]
    assert profile.multithreading.files[0].path == "a.py"
    assert isinstance(results["zzz"][None], AccraError)
    assert list(language.analyze_project({Metrics.PARALLELISM})) == ["par"]

    no_manager = Language(
        LanguageSpec(name="toy", version="1", config=config, analyzers={network})
    )
    assert isinstance(no_manager.analyze_project()["net"][None], AccraError)
    assert (
        Language(LanguageSpec(name="toy", version="1", config=config)).analyze_project()
        == {}
    )


def test_toolchain_path_and_quoting():
    toolchain = Toolchain(path=("/opt/x/bin", "/bin"))
    env = toolchain.applied_to({})
    assert env["PATH"] == "/opt/x/bin:/bin:/usr/bin" or env["PATH"].startswith(
        "/opt/x/bin:/bin"
    )
    assert (
        toolchain.applied_to({"PATH": "/usr/bin:/bin:/opt/x/bin:/bin"})["PATH"]
        == "/opt/x/bin:/bin:/usr/bin"
    )
    odd = Toolchain(
        install=("echo {home}",), environment=(("H", "{home}"),), path=("{home}/b",)
    ).for_home("/tmp/a b; rm")
    assert odd.install == ("echo '/tmp/a b; rm'",)
    assert odd.environment == (("H", "/tmp/a b; rm"),)
    assert odd.path == ("/tmp/a b; rm/b",)
    assert Toolchain(install=("echo {home}",)).for_home("/home/appuser").install == (
        "echo /home/appuser",
    )


def test_profile_patterns_are_validated():
    import pytest

    from accra_language import ScriptProfile

    with pytest.raises(ValueError, match="command_pattern"):
        ScriptProfile(
            language="X", file_suffix=".x", code_fence="x", command_pattern="("
        )
    with pytest.raises(ValueError, match="usage_patterns"):
        ScriptProfile(
            language="X", file_suffix=".x", code_fence="x", usage_patterns=("ok", "[")
        )
