from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from os import PathLike
from .error import ErrorToken
from enum import Enum


class Metrics(Enum):
    LOAD = "load"
    MEMORY = "memory"
    NETWORK = "network"
    PARALLELISM = "parallelism"


class Profile(BaseModel):
    duration_ms: int


class LoadProfile(Profile):
    cpu_percent: float
    gpu_percent: float


class MemoryProfile(Profile):
    peak_memory_mb: float
    total_memory_mb: float


class LibraryUsage(BaseModel):
    name: str
    count: int | None = None


class NetworkProfile(Profile):
    requires_network: bool = False
    dependencies: list[str] = Field(default_factory=list)
    imports: list[LibraryUsage] = Field(default_factory=list)
    api_calls: list[LibraryUsage] = Field(default_factory=list)
    web_frameworks: list[LibraryUsage] = Field(default_factory=list)


class ParallelismUsage(BaseModel):
    used: bool = False
    modules: list[str] = Field(default_factory=list)


class ParallelismProfile(BaseModel):
    multithreading: ParallelismUsage = Field(default_factory=ParallelismUsage)
    multiprocessing: ParallelismUsage = Field(default_factory=ParallelismUsage)


class AnalyzerSpec(BaseModel):
    binary: PathLike[str]
    metrics: set[Metrics] = Field(default_factory=set)


class Analyzer(ABC):
    def __init__(self, spec: AnalyzerSpec):
        self.spec = spec

    @abstractmethod
    def install(self) -> ErrorToken | None: ...

    @abstractmethod
    def analyze(self, args: list[str]) -> set[Profile] | ErrorToken: ...
