import secrets
# create uniqe 8 char string to store as refreh/access token or for any other
def unique_string(byte: int = 8) -> str:
    return secrets.token_urlsafe(byte)