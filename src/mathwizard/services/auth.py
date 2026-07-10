from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher


_password_hash = PasswordHash((BcryptHasher(),))
DUMMY_PASSWORD_HASH = _password_hash.hash("dummy-password")


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)
