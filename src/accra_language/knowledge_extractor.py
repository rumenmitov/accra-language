from abc import ABC
from pathlib import Path
from typing import ClassVar, Final

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from .error import AccraError


class PrologFact(ABC, BaseModel):
    _ESCAPED_CHARS: ClassVar[Final[str]] = ["'"]
    _ESCAPED_CHARS_TABLE: ClassVar[Final[dict[int, str]]] = str.maketrans(
        {char: "\\" + char for char in _ESCAPED_CHARS}
    )

    model_config = ConfigDict(frozen=True)

    @staticmethod
    def _atom(val: str) -> str:
        return f"'{val.translate(PrologFact._ESCAPED_CHARS_TABLE)}'"

    def __str__(self) -> str:
        fact_name: str = type(self).__name__
        fields: dict[str, FieldInfo] = type(self).model_fields

        args: list[str] = [self._atom(str(getattr(self, field))) for field in fields]

        joined_args: str = ", ".join(args)

        return f"{fact_name}({joined_args})"


# TODO In the future, we can gradually add more prolog facts to
# distinguish different errors. Not a prioroty though!
class multilingual_plugin_error(PrologFact, AccraError, BaseModel):
    """Any error caused by erroneous / misconfigured ACCRa plugins
    (e.g. timeout values are too short).

    For errors stemming from the structure of the project itself use
    `project_not_initializable`.

    For errors pertaining to critical
    broken / missing dependencies of the project, use
    `blocking_dependency`.

    For errors occuring during execution of
    the project use the `execution_failure_*` facts.

    """

    plugin: str


class project_not_initializable(PrologFact, AccraError, BaseModel):
    """An error that results in a project that cannot be ran."""


class blocking_dependency(PrologFact, AccraError, BaseModel):
    """A dependency that is not present and could not be installed or ran."""

    dependency: str
    version: str


class execution_failure_missing_file(PrologFact, AccraError, BaseModel):
    """Module failed to run due to a missing file."""

    module: Path
    missing_file: Path


class execution_failure_missing_module(PrologFact, AccraError, BaseModel):
    """Module failed to run due to a missing module."""

    module: Path
    missing_module: Path


class execution_failure_missing_argument(PrologFact, AccraError, BaseModel):
    """Module failed to run due to a missing argument."""

    module: Path
    missing_argument: str


class execution_failure_timeout(PrologFact, AccraError, BaseModel):
    """Module failed to terminate in the configured time."""

    module: Path
    missing_argument: str


class execution_failure_other(PrologFact, AccraError, BaseModel):
    """Module failed to run successfully for some other reason."""

    module: Path


class known_blocked_dependency(PrologFact, BaseModel):
    """Any dependency that is known to be unsupported by ACCRa."""

    dependency: str
    version: str


class has_main(PrologFact, BaseModel):
    """
    A file that has a language-specific symbol (e.g. main())
    designating it as an entrypoint.

    """

    file: Path


class uses_input_method(PrologFact, BaseModel):
    """
    An input method that the file accepts, e.g. argv, interactive
    (i.e. waits for user to type in input), etc.

    """

    file: Path
    method: str


class documented_entry_point(PrologFact, BaseModel):
    """An entry point specified in the documentation."""

    entry_point: Path


class public_module(PrologFact, BaseModel):
    """A project module intended to be used in other projects, i.e. an exported module."""

    module: Path


class exported_symbol(PrologFact, BaseModel):
    """A symbol exported as part of the project's API.

    `symbol_kind` describes the symbol's category, e.g. function, class, variable, etc.

    """

    module: Path
    symbol: str
    symbol_kind: str


class symbol_has_docstring(PrologFact, BaseModel):
    """A documented symbol."""

    module: Path
    symbol: str


class symbol_signature(PrologFact, BaseModel):
    """A symbol's function signature, in the case that the symbol is a function."""

    module: Path
    symbol: str
    signature: str


class symbol_param_annotated(PrologFact, BaseModel):
    """A parameter that is type-annotated in the function."""

    module: Path
    function: str
    parameter: str


class driver_symbol(PrologFact, BaseModel):
    """A symbol related to the entry point of the program, rather than the exposed API, e.g. main()."""

    module: Path
    symbol: str


class pure_side_effect_symbol(PrologFact, BaseModel):
    """A function symbol of a function with no return value."""

    module: Path
    symbol: str


class imports_module(PrologFact, BaseModel):
    """A module importing another module."""

    module: Path
    imported_module: Path


class entry_point_imports_module(PrologFact, BaseModel):
    """A module imported by an entry point."""

    entry_point: Path
    imported_module: Path


class source_file(PrologFact, BaseModel):
    """A source file of a given programming language."""

    language: str
    path: Path


class exe_file(PrologFact, BaseModel):
    """An executable file."""

    path: Path


class results_file(PrologFact, BaseModel):
    path: Path


class defines_function(PrologFact, BaseModel):
    """A function defined in a module."""

    module: Path
    function_name: str


class defines_class(PrologFact, BaseModel):
    """A class defined in a module."""

    module: Path
    class_name: str


class readme_has_code_block(PrologFact, BaseModel):
    """A code block found in the README."""

    language: str


class readme_mentions_source_file(PrologFact, BaseModel):
    """A source file mentioned in the README."""

    language: str
    source_file: Path


class readme_mentions_command(PrologFact, BaseModel):
    """A command found in the README."""

    command: str


class readme_mentions_symbol(PrologFact, BaseModel):
    """A symbol mentioned in the README."""

    symbol: str


class doc_has_code_block(PrologFact, BaseModel):
    """A code block found in the documentation."""

    doc: Path
    language: str


class doc_mentions_source_file(PrologFact, BaseModel):
    """A source file mentioned in the documentation."""

    doc: Path
    language: str
    source_file: Path


class doc_mentions_command(PrologFact, BaseModel):
    """A command found in the documentation."""

    doc: Path
    command: str


class doc_mentions_symbol(PrologFact, BaseModel):
    """A symbol mentioned in the documentation."""

    doc: Path
    symbol: str


class doc_command_for_target(PrologFact, BaseModel):
    """A command in the documentation that runs one of the project's targets."""

    doc: Path
    module: Path
    command: str


class cli_help_available(PrologFact, BaseModel):
    """The entry point offers a help flag."""

    entry_point: Path


class cli_option(PrologFact, BaseModel):
    """An option accepted by the entry point."""

    entry_point: Path
    flag: str
    value_type: type
    required: bool


class cli_positional(PrologFact, BaseModel):
    """A positional argument accepted by the entry point."""

    entry_point: str
    argument: str
    argument_type: type


class cli_subcommand(PrologFact, BaseModel):
    """A subcommand accepted by the entry point."""

    entry_point: str
    subcommand: str
    description: str


class stdlib_module(PrologFact, BaseModel):
    """A module included in a language's standard library and should not be explicitly installed."""

    name: str


class hardware_requirement(PrologFact, BaseModel):
    """The project requires specific hardware drivers."""

    requirement: str
