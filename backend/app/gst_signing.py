import os
import hmac
import hashlib

def _get_secret() -> bytes:
    return os.environ.get("GST_SIGNING_KEY", "dev-secret-key").encode()

def sign_payload(text: str) -> str:
    """Return hex HMAC-SHA256 signature for the provided text."""
    secret = _get_secret()
    return hmac.new(secret, text.encode(), hashlib.sha256).hexdigest()

def verify_signature(text: str, signature: str) -> bool:
    secret = _get_secret()
    expected = hmac.new(secret, text.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
