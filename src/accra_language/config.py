from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    cwd: Path | None = None
    env: Mapping[str, str] | None = None
    shell: bool = False
    timeout: float | None = None
