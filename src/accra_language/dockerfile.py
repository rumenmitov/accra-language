from typing import NewType

DockerfileInstruction = NewType("DockerfileInstruction", str)


def generate_dockerfile(instructions: list[DockerfileInstruction]) -> str | None:
    dockerfile: str = ""

    if not instructions:
        return None

    for instruction in instructions:
        dockerfile.append(instruction + "\n")

    return dockerfile
