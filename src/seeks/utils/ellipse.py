def ellipse(value: str, length: int = 40) -> str:
    return value[:length] + "..." if len(value) > length else value
