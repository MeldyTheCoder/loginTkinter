import hmac
from hashlib import sha256


class HashTools:
    secret = 'password'
    digest = sha256

    @classmethod
    def make_hash(cls, text: str | bytes):
        secret = cls.secret

        if isinstance(text, str):
            text = text.encode()

        if isinstance(secret, str):
            secret = secret.encode()

        return hmac.new(secret, text, digestmod=cls.digest).hexdigest()

    @classmethod
    def compare_digest(cls, digest: str | bytes, text: str | bytes):
        new_hash = cls.make_hash(text)
        return hmac.compare_digest(digest, new_hash)