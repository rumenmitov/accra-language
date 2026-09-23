from pydantic import BaseModel


class AccraLanguageErrorType(Enum):
    InstallError = (1,)
    BuildError = (auto(),)
    RunError = (auto(),)
    AnalysisError = auto()


class AccraLanguageError(BaseModel):
    error: AccraLanguageErrorType
    message: str | None
