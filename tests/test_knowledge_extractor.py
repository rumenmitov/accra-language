"""The Prolog facts: how errors and knowledge about the build are reported,
and how `AccraResult` collects them."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from accra_language import (
    AccraError,
    AccraResult,
    blocking_dependency,
    execution_failure,
    execution_success,
    multilingual_plugin_error,
    project_not_initializable,
    public_symbol,
)
from accra_language.knowledge_extractor import PrologFact


def test_error_facts_are_accra_errors():
    for fact in (
        multilingual_plugin_error(plugin="p", error="m"),
        project_not_initializable(error="m"),
        blocking_dependency(dependency="d", version="1", error="m"),
        execution_failure(module=Path("m.py"), error="m"),
    ):
        assert isinstance(fact, AccraError)
        assert isinstance(fact, PrologFact)
        assert fact.error == "m"


def test_knowledge_facts_are_not_errors():
    fact = execution_success(module=Path("m.py"))
    assert isinstance(fact, PrologFact)
    assert not isinstance(fact, AccraError)


def test_facts_render_as_prolog_atoms():
    assert str(multilingual_plugin_error(plugin="p", error="m")) == (
        "multilingual_plugin_error('m', 'p')"
    )
    assert str(blocking_dependency(dependency="d", version="1", error="m")) == (
        "blocking_dependency('m', 'd', '1')"
    )
    assert str(execution_failure(module=Path("a/b.py"), error="m")) == (
        "execution_failure('m', 'a/b.py')"
    )
    assert str(public_symbol(module=Path("a.py"), symbol="f", symbol_kind="fn")) == (
        "public_symbol('a.py', 'f', 'fn')"
    )


def test_fact_atoms_escape_quotes():
    fact = project_not_initializable(error="can't happen")
    assert str(fact) == "project_not_initializable('can\\'t happen')"


def test_facts_are_frozen():
    fact = project_not_initializable(error="m")
    with pytest.raises(ValidationError):
        fact.error = "other"


def test_facts_are_hashable_and_compared_by_value():
    same = {project_not_initializable(error="m"), project_not_initializable(error="m")}
    different = project_not_initializable(error="other")
    assert len(same) == 1
    assert same == {project_not_initializable(error="m")}
    assert different not in same
    assert {
        execution_success(module=Path("a.py")),
        execution_success(module=Path("b.py")),
    } == {
        execution_success(module=Path("a.py")),
        execution_success(module=Path("b.py")),
    }


def test_result_collects_facts_and_flags_abort():
    fact = project_not_initializable(error="m")
    result = AccraResult(facts={fact}, abort=True)

    assert fact in result.facts
    assert result.abort


def test_result_extend_merges_facts_and_abort():
    first = AccraResult(facts={project_not_initializable(error="a")})
    second = AccraResult(
        facts={
            project_not_initializable(error="b"),
            project_not_initializable(error="a"),
        },
        abort=True,
    )

    first.extend(second)

    assert len(first.facts) == 2
    assert first.abort


def test_result_extend_keeps_abort_false_when_all_parts_continue():
    result = AccraResult()
    result.extend(AccraResult())

    assert not result.abort and not result.facts
