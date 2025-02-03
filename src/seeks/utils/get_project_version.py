import re


def get_project_version() -> str:
    version_pattern = r'^version\s*=\s*"(\d+\.\d+\.\d+)"'

    with open("pyproject.toml", "r") as file:
        content = file.read()
        match = re.search(version_pattern, content, re.MULTILINE)

        if match:
            return match.group(1)

    return "0.0.0"
