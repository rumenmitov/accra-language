from pydantic import NewType

from .dockerfile import DockerfileInstruction
from .errors import AccraError

AccraResult = NewType("AccraResult", list[DockerfileInstruction] | AccraError)
