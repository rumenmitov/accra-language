from typing import NewType

from .dockerfile import DockerfileInstruction
from .error import AccraError

AccraResult = NewType("AccraResult", list[DockerfileInstruction] | AccraError)
