import sys
from cryptography.fernet import Fernet


def generate_key() -> str:
    """Generate and return a new Fernet key as a string."""
    return Fernet.generate_key().decode()


class Encryptor:
    def __init__(self, key: str = ""):
        if not key:
            print(
                "[ERROR] FERNET_KEY not set in .env. "
                "Run: python mailer.py --keygen",
                file=sys.stderr,
            )
            sys.exit(1)
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()
