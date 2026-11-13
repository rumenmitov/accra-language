from typing import Self

from pydantic import BaseModel, Field

from .dockerfile import Dockerfile
from .knowledge_extractor import PrologFact


class AccraResult(BaseModel):
    """Contains the dockerfile instructions, and a set of facts about the
    build process.

    If the `abort` field is True, an unrecoverable error was
    encountered such that the plugin cannot execute any further
    procedures.

    """

    dockerfile: Dockerfile = Field(default_factory=Dockerfile)
    facts: set[PrologFact] = Field(default_factory=set)
    abort: bool = False

    def extend(self, other: Self):
        self.dockerfile.extend(other.dockerfile)
        self.facts.update(other.facts)
        self.abort &= other.abort
