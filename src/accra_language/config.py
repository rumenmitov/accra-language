from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    cwd: Path | None = None
    env: Mapping[str, str] | None = None
    shell: bool = False
    timeout: float | None = None

    def get_subprocess_config(self) -> dict:
        return {
            **self.model_dump(),
            "capture_output": True,
            "check": True,
            "text": True,
        }
