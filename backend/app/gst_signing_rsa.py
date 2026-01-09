from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from typing import Tuple

def generate_rsa_keypair(bits: int = 2048) -> Tuple[bytes, bytes]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits, backend=default_backend())
    pem_priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_priv, pem_pub

def sign_with_private(pem_private: bytes, message: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(pem_private, password=None, backend=default_backend())
    sig = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return sig

def verify_with_public(pem_public: bytes, message: bytes, signature: bytes) -> bool:
    public_key = serialization.load_pem_public_key(pem_public, backend=default_backend())
    try:
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False
