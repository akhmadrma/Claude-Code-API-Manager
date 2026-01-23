"""Encryption utilities for backup files."""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os


class CryptoManager:
    """Handle encryption and decryption for backups."""

    def __init__(self, password: str, salt: Optional[bytes] = None):
        """
        Initialize crypto manager.

        Args:
            password: Password for encryption/decryption
            salt: Salt for key derivation (generated if not provided)
        """
        self.password = password.encode() if isinstance(password, str) else password
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

    def _derive_key(self) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data with salt prepended
        """
        encrypted = self.fernet.encrypt(data)
        # Prepend salt for decryption
        return self.salt + encrypted

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data.

        Args:
            data: Data to decrypt (salt + encrypted data)

        Returns:
            Decrypted data
        """
        # Extract salt from first 16 bytes
        salt = data[:16]
        encrypted_data = data[16:]

        # Reinitialize fernet with extracted salt
        self.salt = salt
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

        return self.fernet.decrypt(encrypted_data)
