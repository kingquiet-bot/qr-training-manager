"""
Encryption utilities for multi-tenant credential storage.
Uses Fernet (AES-128-CBC) symmetric encryption with a master secret.
"""

import os
import base64
import hashlib


def _get_fernet():
    """Derive a Fernet key from MASTER_SECRET env var."""
    from cryptography.fernet import Fernet

    secret = os.environ.get("MASTER_SECRET", "")
    if not secret:
        raise RuntimeError(
            "MASTER_SECRET environment variable is required for credential encryption. "
            "Generate one with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    # Hash the secret to get a consistent 32-byte key
    key = hashlib.sha256(secret.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt(plaintext: str) -> str:
    """Encrypt a string value. Returns a token string."""
    if not plaintext:
        return ""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a token string back to plaintext."""
    if not ciphertext:
        return ""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
