import hashlib


def normalize_email(email: str) -> str:
    return email.strip().lower()


def email_key(email: str) -> str:

    normalized = normalize_email(email)

    email_hash = hashlib.sha256(
        normalized.encode()
    ).hexdigest()

    return email_hash