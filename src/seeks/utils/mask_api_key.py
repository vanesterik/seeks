def mask_api_key(api_key: str) -> str:
    """
    Mask API key with asterisks for security

    Params
    ------
    - api_key (str): API key to mask.

    Returns
    -------
    - str: Masked API key.

    """
    allowed_chars = 4
    star_chars = 13
    return f"{api_key[:allowed_chars]}...{'*' * star_chars}"
