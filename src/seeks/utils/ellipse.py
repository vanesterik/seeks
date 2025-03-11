from typing import Union


def ellipse(value: Union[str, None], length: int = 40) -> Union[str, None]:

    if value is None:
        return None

    return value[:length] + "..." if len(value) > length else value
