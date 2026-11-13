# accra-language public API

accra-language is the common interface for plugins of every language
(compiled, interpreted, VM-based). It only holds what is language-agnostic:
what a language's interpreter, environment, imports or system packages are is
decided by the plugin, and running, tearing down and recording the build is
ACCRa's job.

Everything is exported from `accra_language`.

A guide for plugin authors, with what ACCRa does with each hook, is in the ACCRa repository ([github.com/GiancarloSucci/ACCRa](https://github.com/GiancarloSucci/ACCRa)) at `docs/language-plugin-contract.md`.

## Models

- `Config`: `repo`, `cwd`, `env`, `shell`, `timeout` (per subprocess), `build_timeout` (whole build, seconds; 0 or None means no budget), `language_version` (caller-chosen version, skips selection), `image_workdir` (the project's directory in the composed image, `/project` by default; the caller clones there and makes it the working directory). `env` is how the caller passes environment variables to a plugin. A `Config` with an `env` is not hashable (the mapping is not). `shell` defaults to False.
- `Dependency`: `name` and `version`, both opaque strings that only the plugin interprets. `name` is the identifier as the manifest wrote it (extras, VCS, URL or path specs included); `version` is the constraint in the language's native syntax with its operator, empty when unconstrained. Frozen, hashable and ordered by `(name, version)`.
- `Dockerfile`: the plugin's part of an image: `pre_dependencies_installation` (installing the language's toolchain on the caller's Debian-based base image and setting up the environment), `dependencies_installation` and `post_dependencies_installation` (the project install); `project_steps()` joins them. The steps that are the same for every language (`FROM`, cloning, the working directory, the user) are the caller's, which composes one image from all present languages' parts on its own base image.
- `AccraResult`: `dockerfile` (a `Dockerfile`), `facts` (the `PrologFact`s recorded during the build, errors included) and `abort`. `abort` is True when an unrecoverable error was encountered, such that the plugin cannot execute any further procedures. `extend(other)` merges another result's dockerfile lines and facts, and aborts when either result does.
- `EntryPoint`: `name`, `kind` (the plugin's own category, e.g. `script`, `module`, `binary`), `command` (the argv; the caller appends the arguments), `cwd`, `path` (the source file, if any). Frozen.
- `Toolchain`: `executables` (commands needed on PATH), `packages` (Debian packages that provide them or that builds need), `notes`, and how to install them: `install` (POSIX `sh` commands, run in order by the user that runs the plugin on a Debian host where `packages` are installed, each safe to run again), `environment` ((name, value) pairs the executables need) and `path` (directories to put in front of `PATH`); in those three, `{home}` stands for that user's home directory. `for_home(home)` renders it (in `install` the home is shell-quoted with `shlex.quote`, in `environment` and `path` it is inserted as is); `applied_to(env)` returns `env` with the environment set and the path in front of `PATH` (the toolchain's directories first, each once, even when `PATH` had them later; without a `PATH` in `env` it starts from `os.defpath`). Frozen; every field defaults to empty.
- `ScriptProfile`: how programs in the language are written and run, for a caller that describes them to a language model (one that writes a usage script, or works out an entry point's inputs): `language` (its name in prose), `file_suffix`, `code_fence` (the tag of a fenced code block), `conventions` (the language's own rules for a usage script, one sentence each), `run_command` (how a source file is run, `{file}` standing for it, e.g. `python {file}`; empty when a file is not run by itself), `cli_frameworks` (the command-line libraries whose `--help` output an entry point prints), `project_files` (the root files that say how the project is set up), `command_pattern` (a regular expression matching, in documentation, the command that runs a source file), `usage_patterns` (regular expressions, matched case-insensitively, marking documentation that tells how to install or run the language's programs) and `package_registry` (the name of the registry its packages are published to). Frozen; `language`, `file_suffix` and `code_fence` are required, the others default to empty.

## Prolog facts

Results and build knowledge are reported as `PrologFact`s: frozen, hashable
pydantic models, each rendering to a Prolog atom with `str()` (e.g.
`project_not_initializable('no manifests present')`; apostrophes are escaped).
Facts that report errors are also `AccraError`s.

- `AccraError`: the base of every error fact, with one field, `error` (what went wrong). It is abstract: errors are always one of the facts below.
- `multilingual_plugin_error(plugin, error)`: any error caused by an erroneous or misconfigured plugin (e.g. timeout values are too short).
- `project_not_initializable(error)`: something is wrong with the project itself, so it cannot be initialized or run (no manifests, no agreed language version, the build time budget ran out).
- `blocking_dependency(dependency, version)`: a critical dependency is broken or missing.
- `execution_failure_missing_file(module, missing_file)`: a module failed to run for lack of a file.
- `execution_failure_missing_module(module, missing_module)`: a module failed to run for lack of another module.
- `execution_failure_missing_argument(module, missing_argument)`: a module failed to run for lack of an argument.
- `execution_failure_timeout(module, missing_argument)`: a module did not terminate within the configured time.
- `execution_failure_other(module)`: a module failed to run for any other reason.

The remaining facts carry knowledge for reasoning (not errors): `known_blocked_dependency`, `has_main`, `uses_input_method`, `documented_entry_point`, `public_module`, `exported_symbol`, `symbol_has_docstring`, `symbol_signature`, `symbol_param_annotated`, `driver_symbol`, `pure_side_effect_symbol`, `imports_module`, `entry_point_imports_module`, `source_file`, `exe_file`, `defines_function`, `defines_class`, `readme_has_code_block`, `readme_mentions_source_file`, `readme_mentions_command`, `readme_mentions_symbol`, `doc_has_code_block`, `doc_mentions_source_file`, `doc_mentions_command`, `doc_mentions_symbol`, `doc_command_for_target`, `cli_help_available`, `cli_option`, `cli_positional`, `cli_subcommand`, `stdlib_module`, `hardware_requirement`.

Their arguments: `known_blocked_dependency(dependency, version)` is a dependency known to be unsupported by ACCRa. `has_main(file)` marks a file with a language-specific symbol (e.g. `main()`) designating it as an entry point; `uses_input_method(file, method)` gives an input method the file accepts (e.g. argv, interactive). `documented_entry_point(entry_point)` is an entry point specified in the documentation. `public_module(module)` is a module intended to be used in other projects; `exported_symbol(module, symbol, symbol_kind)` is a symbol exported as part of the project's API (`symbol_kind` is its category: function, class, variable, ...). `symbol_has_docstring(module, symbol)` is a documented symbol; `symbol_signature(module, symbol, signature)` gives a function symbol's signature; `symbol_param_annotated(module, function, parameter)` is a type-annotated parameter. `driver_symbol(module, symbol)` is a symbol related to the program's entry point rather than its exposed API (e.g. `main()`); `pure_side_effect_symbol(module, symbol)` is a function symbol with no return value. `imports_module(module, imported_module)` is a module importing another; `entry_point_imports_module(entry_point, imported_module)` is a module an entry point imports. `source_file(language, path)` is a source file of a programming language; `exe_file(path)` an executable. `defines_function(module, function_name)` and `defines_class(module, class_name)` are what a module defines. `readme_has_code_block(language)`, `readme_mentions_source_file(language, source_file)`, `readme_mentions_command(command)` and `readme_mentions_symbol(symbol)` are what the README holds. `doc_has_code_block(doc, language)`, `doc_mentions_source_file(doc, language, source_file)`, `doc_mentions_command(doc, command)` and `doc_mentions_symbol(doc, symbol)` are what a documentation file holds; `doc_command_for_target(doc, module, command)` is a command in the documentation that runs one of the project's targets. `cli_help_available(entry_point)` says an entry point offers a help flag; `cli_option(entry_point, flag, value_type, required)`, `cli_positional(entry_point, argument, argument_type)` and `cli_subcommand(entry_point, subcommand, description)` are what its command line accepts. `stdlib_module(name)` is a module of the language's standard library that should not be installed explicitly; `hardware_requirement(requirement)` is a hardware driver the project needs.

## Language

`Language(spec, env_manager=None)`.

A plugin's `Language` subclass is constructed by its caller as `YourLanguage(config: Config, env_manager=None)`, and builds its own `LanguageSpec` from the `Config`. ACCRa calls it with one positional `Config`, on a project path that may not exist yet and with `env=None` (to read the toolchain before the tools are installed, and to probe `is_present()`), so the constructor must succeed with a missing `cwd`, `env=None` and none of the toolchain installed. It does read files: each `EnvironmentManager` constructor calls its manifests' `detect()`, which must be cheap, read-only and must not raise. Without an `env_manager` argument, the env manager is selected lazily by the first call that needs one, as described under Models; until then `env_manager` is None. A language without any env manager gets a `multilingual_plugin_error` fact from `detect()` and an aborted `AccraResult` from `build()`. Neither the library nor a plugin logs or swallows exceptions: everything a caller needs comes back in the return values (a fact, or `AccraResult.facts`), and a plugin's hooks should not raise. An exception that does occur is a bug, and it propagates to the caller, which decides what a failed run means. A manifest's `get_supported_language_versions()` may return any set, or an `AccraError`, which is passed through; anything else is a `multilingual_plugin_error` naming the manifest.

- `is_present()`: whether the project holds code of the language; cheap and read-only (no version selection, no tools, no writes). Default: a supported env manager found one of its manifests; a plugin with a catch-all manifest overrides it
- `detect()`: selects the env manager if no earlier call did, and the language version; `bool | AccraError`
- `build()`: `AccraResult`; honours `Config.build_timeout` between steps and dependencies. The project's own install or build is part of it (the env manager's `post_dependencies_installation()`). When a step returns an aborted result (or the budget runs out before a step), the build stops and the recorded facts say why
- `manifest_paths()`: the files of the present manifests
- `missing_tools()`: the `toolchain.executables` that are not on PATH (`Config.env`'s, else the process's)
- `analyze_project(metrics=None, runs=())`: runs every analyzer measuring one of `metrics` (all when None) on the project and on `runs` (`AnalysisRun`s, for the analyzers that measure runs); `dict` of analyzer name to its `AnalysisResults` (`dict` keyed by entry point, None for a measure of the whole project, to `set[Profile]` or `AccraError`), in name order. Selects the env manager when no earlier call did; an analyzer sets itself up (e.g. a profiler) and keeps that out of the project's environment
- `script_profile()`, `check_script(path)`, `read_script(source)`: usage scripts in the language. The profile (a `ScriptProfile`, None when the plugin has no usage scripts), a check that the script is valid without running it (None, else a `multilingual_plugin_error`), and what the script does with the project's public symbols, read without running it. They need no build. Unsupported by default
- `env_manager`: the caller's, or the one the first call that needs it selected; None before that

`LanguageSpec.toolchain` (a `Toolchain`) declares the system tools the plugin needs; `LanguageSpec.analyzers` holds its analyzers.

## EnvironmentManager

A plugin must implement `pre_dependencies_installation()` and `_install_dependency()`; it may override `post_dependencies_installation()` (the project's own install or build, with its Dockerfile lines) and give its `EnvironmentManagerSpec` a `version_order`.

- `present_manifests`, `selected_language_version`, `supported_language_versions()` (what every present manifest agrees on; `project_not_initializable` when there are no manifests or they do not agree on a version), `ranked_language_versions(order=None)` (those versions, most preferred first, by `order`, else the spec's `version_order`, else alphabetically; a version the order leaves out comes last and one it invents is dropped) and `select_language_version(order=None)` (the first of them; `order` is a callback taking the set of versions and returning them ordered, so the plugin, or a caller that retries without a version that failed, defines what "best" means)
- `_get_dependencies()`, `_install_dependency(dependency)`, `dependencies_installation()`: the plugin contract for collecting and installing dependencies; `_get_dependencies()` collects every present manifest's `extract_dependencies()` into one set. A dependency install whose result aborts stops the remaining ones, and the build stops too
- `subprocess_timeout()`: pass it to every `subprocess.run`, so `Config.build_timeout` caps each call
- `start_build_budget()`, `end_build_budget()`, `remaining_build_time()`, `build_budget_exhausted()`

## Analyzer

`Analyzer(spec)` with `AnalyzerSpec`: `name`, `config`, `metrics` (`Metrics`: load, memory, network, parallelism). It measures a built project from its sources, from runs of its entry points, or both. A plugin implements one method:

- `analyze_project(env_manager, runs=())`: measures the project of `env_manager` (`Config.cwd`, the manifests' dependencies) and returns an `AnalysisResults`: a `dict` keyed by entry point (None for a measure of the whole project, as a static analysis gives, which needs no `runs`) to `set[Profile] | AccraError`. An analyzer that measures runs gives one result per run, keyed by the run's entry point (one run per entry point), and nothing when there are no runs. A run that ended before it could be measured gives an `AccraError`. The analyzer makes itself usable (e.g. installs a profiler) without touching the project's own environment or dependencies

An `AnalysisRun` is one run to measure: `entry_point`, `args`, `env`, `timeout` and `output_dir` (where the reports go; default a new temporary directory).

The caller chooses what to run and with which arguments. The profiles are `MemoryProfile` (`peak_memory_mb`, `total_memory_mb`), `LoadProfile` (`cpu_percent`, `gpu_percent`), `NetworkProfile` (`requires_network`, `dependencies`, and `imports`, `api_calls`, `web_frameworks` as `LibraryUsage(name, count)`) and `ParallelismProfile` (`multithreading` and `multiprocessing`, each a `ParallelismUsage`: `used`, `modules`, `files` as `FileModules(path, modules)`), all with `duration_ms`, `exit_code` (set when the run failed but could still be measured) and `report` (the analyzer's report file, if any); frozen.

## Manifest

`spec`, `detect()` (must not raise, and must be cheap and read-only: `Language.is_present()` relies on it), `path()` (the manifest's file, `cwd/<spec.name>` when it exists), `extract_dependencies()` (the manifest's dependencies as a set, empty when there are none) and `get_supported_language_versions()` (the versions the manifest allows, or an `AccraError`).

## Left to plugins and ACCRa

Not part of this interface: observed imports, teardown, and readiness classification of dependencies.

## Security obligations

- Never pass dependency strings (or any manifest-derived text) through a shell: run commands as argument lists. `Config.shell` is False by default; set it only for a command line the plugin fully controls.
- Quote every argument you put into a Dockerfile instruction, and keep control characters out of them.
- `Toolchain.install` commands are trusted: they run as `sh` at image build, as the user that runs the plugin, so they must come only from the plugin itself. `for_home` shell-quotes the home it substitutes.
- `ScriptProfile.command_pattern` and `usage_patterns` must compile as Python regular expressions; construction raises a `ValueError` naming the field otherwise.
