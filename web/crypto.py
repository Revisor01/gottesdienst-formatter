#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fernet-Verschluesselung fuer sensitive Datenbank-Felder (z.B. SMTP-Passwort).

Schluessel wird deterministisch aus SECRET_KEY abgeleitet — kein separater KEY noetig.
"""
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Statischer Salt — reicht fuer diesen Anwendungsfall (kein benutzerspezifischer Kontext)
_SALT = b'gottesdienst-formatter'
_ITERATIONS = 480000


def _get_fernet_key(secret_key: str) -> bytes:
    """Leitet einen deterministischen 32-Byte Fernet-Key aus SECRET_KEY ab."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=_ITERATIONS,
    )
    key_bytes = kdf.derive(secret_key.encode('utf-8'))
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_value(value: str, secret_key: str) -> str:
    """Verschluesselt einen Klartext-String mit Fernet.

    Args:
        value: Zu verschluesselnder Klartext.
        secret_key: SECRET_KEY aus app.config (z.B. current_app.config['SECRET_KEY']).

    Returns:
        Base64-kodierter verschluesselter String.
    """
    fernet = Fernet(_get_fernet_key(secret_key))
    return fernet.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_value(encrypted: str, secret_key: str) -> str:
    """Entschluesselt einen Fernet-verschluesselten String.

    Args:
        encrypted: Verschluesselter Base64-String (von encrypt_value).
        secret_key: SECRET_KEY aus app.config (z.B. current_app.config['SECRET_KEY']).

    Returns:
        Klartext-String.
    """
    fernet = Fernet(_get_fernet_key(secret_key))
    return fernet.decrypt(encrypted.encode('utf-8')).decode('utf-8')
