def mask_api_key(api_key: str) -> str:
    allowed_chars = 4
    star_chars = 20
    return f"{api_key[:allowed_chars]}{'*' * star_chars}"
