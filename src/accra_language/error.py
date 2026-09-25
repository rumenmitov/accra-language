from abc import ABC

from pydantic import BaseModel


class AccraError(ABC, BaseModel):
    message: str


class AccraInstallError(AccraError):
    pass


class AccraBuildError(AccraError):
    pass


class AccraRunError(AccraError):
    pass


class AccraAnalysisError(AccraError):
    pass
