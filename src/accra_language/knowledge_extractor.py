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
    """Any error caused by erroneous / misconfigured ACCRa plugins.

    For errors stemming from the structure of the project itself use
    `project_not_initializable`.

    For errors pertaining to critical
    broken / missing dependencies of the project, use
    `blocking_dependency`.

    For errors occuring during execution of
    the project use `execution_failure`.

    """

    plugin: str


class project_not_initializable(PrologFact, AccraError, BaseModel):
    """When something is wrong with the project itself."""


class blocking_dependency(PrologFact, AccraError, BaseModel):
    dependency: str
    version: str


class execution_failure(PrologFact, AccraError, BaseModel):
    module: Path


class execution_success(PrologFact, BaseModel):
    module: Path


class candidate_entry_point(PrologFact, BaseModel):
    file: Path


class weak_candidate(PrologFact, BaseModel):
    file: Path


class preferred_entry_point(PrologFact, BaseModel):
    file: Path


class likely_input_extension(PrologFact, BaseModel):
    file: Path
    ext: str


class showcase_api_target(PrologFact, BaseModel):
    module: Path
    symbol: str


class preferred_showcase_symbol(PrologFact, BaseModel):
    module: Path
    symbol: str


class public_module(PrologFact, BaseModel):
    module: Path


class public_symbol(PrologFact, BaseModel):
    module: Path
    symbol: str
    symbol_kind: str


class symbol_has_docstring(PrologFact, BaseModel):
    module: Path
    symbol: str


class symbol_signature(PrologFact, BaseModel):
    module: Path
    symbol: str
    signature: str


class symbol_param_annotated(PrologFact, BaseModel):
    module: Path
    symbol: str
    parameter: str


class driver_symbol(PrologFact, BaseModel):
    module: Path
    symbol: str


class pure_side_effect_symbol(PrologFact, BaseModel):
    module: Path
    symbol: str


class exported(PrologFact, BaseModel):
    module: Path
    symbol: str


class imported(PrologFact, BaseModel):
    module: Path
    imported_module: Path


class source_file(PrologFact, BaseModel):
    language: str
    path: Path


class exe_file(PrologFact, BaseModel):
    path: Path


class results_file(PrologFact, BaseModel):
    path: Path


class defines_function(PrologFact, BaseModel):
    module: Path
    function_name: str


class defines_class(PrologFact, BaseModel):
    module: Path
    class_name: str


class doc_has_code_block(PrologFact, BaseModel):
    doc: Path
    language: str


class doc_mentions_source_file(PrologFact, BaseModel):
    doc: Path
    language: str
    source_file: Path


class doc_mentions_command(PrologFact, BaseModel):
    doc: Path
    command: str


class cli_help_available(PrologFact, BaseModel):
    module: Path


class cli_option(PrologFact, BaseModel):
    entry_point: str
    flag: str
    value_type: type
    required: bool


class cli_positional(PrologFact, BaseModel):
    entry_point: str
    name: str
    value_type: type


class stdlib_module(PrologFact, BaseModel):
    name: str


class hardware_requirement(PrologFact, BaseModel):
    module: Path
    requirement: str
