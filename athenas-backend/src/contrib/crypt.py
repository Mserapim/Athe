# -*- coding:utf-8 -*-

import os
import pickle
import base64
import json

from Crypto.Cipher import AES
from django.conf import settings
from contrib.utils import getLogger
from django.core.cache import cache

log = getLogger(__name__)


class Cipher(object):

    def __init__(self, algorithm, mode, secret, secret_part=""):
        self.__secret = secret
        self.__secret_part = secret_part
        self.__cipher = algorithm.new(
            self.__secret.encode() if isinstance(self.__secret, str) else self.__secret,
            mode,
        )

    def __add_padding(self, plain):
        block_size = 32
        plain = plain.encode() if isinstance(plain, str) else plain
        return plain + (b"\0" * (block_size - len(plain) % block_size))

    def __remove_padding(self, plain):
        return plain[0 : plain.index(b"\0")]

    def encrypt(self, plain):
        plain = plain.encode() if isinstance(plain, str) else plain
        return base64.b64encode(self.__cipher.encrypt(self.__add_padding(plain)))

    def decrypt(self, crypted, clear_padding=True):
        if clear_padding:
            return self.__remove_padding(
                self.__cipher.decrypt(base64.b64decode(crypted))
            )

        return self.__cipher.decrypt(base64.b64decode(crypted))

    @property
    def secret(self):
        return self.__secret

    @property
    def secret_part(self):
        return self.__secret_part

    def b64_encrypt(self, plain):
        encrypted = self.encrypt(plain)
        return base64.b64encode(encrypted).decode("utf-8")

    def b64_decrypt(self, crypted):
        crypted = base64.b64decode(crypted)
        decrypted = self.decrypt(crypted=crypted, clear_padding=True)
        return decrypted.decode("utf-8")


class MemoryCipherManager(object):

    __instances = {}
    __secret_part = ""
    __mode = getattr(settings, "CIPHER_MODE", AES.MODE_ECB)
    __algorithm = getattr(settings, "CIPHER_ALGORITHM", AES)
    __key_length = getattr(settings, "CIPHER_SECRET_LENGTH", 32)

    def __init__(self):
        raise Exception("Don't do that! Use the class method instance.")

    @classmethod
    def create_secret_key(cls, key_length, secret_part=""):
        return cls.__create_secret_key(key_length, secret_part)

    @classmethod
    def __create_secret_key(cls, key_length, secret_part=""):
        secret = secret_part.encode()

        if key_length > len(secret):
            secret += base64.b64encode(os.urandom(key_length - len(secret_part)))

        if len(secret) > key_length:
            secret = secret[:key_length]

        return secret

    @classmethod
    def config(cls, algorithm=AES, key_length=32, mode=AES.MODE_ECB, secret_part=""):
        cls.__algorithm = algorithm
        cls.__key_length = key_length
        cls.__secret_part = secret_part
        cls.__mode = mode
        return cls

    @classmethod
    def instance(cls, name="default", keypass=None):

        key = "cipher-%s" % name
        if not cache.get(key):
            cipher_keys_dir = os.path.join(settings.CACHE_BASE, "cipher-keys")
            if not os.path.exists(cipher_keys_dir):
                os.makedirs(cipher_keys_dir)

            cipher_key_file = os.path.join(cipher_keys_dir, key)
            if not os.path.exists(cipher_key_file):
                secret = cls.__create_secret_key(cls.__key_length, cls.__secret_part)

                log.info(secret)
                keys = {"secret": secret, "secret_part": cls.__secret_part}
                pickled = pickle.dumps(keys)

                with open(cipher_key_file, "wb") as f:
                    log.debug(keypass)
                    encrypted_keys = Cipher(
                        cls.__algorithm, cls.__mode, keypass
                    ).encrypt(pickled)
                    f.write(encrypted_keys)

            with open(cipher_key_file) as f:
                encrypted = f.read()
                pickled = Cipher(cls.__algorithm, cls.__mode, keypass).decrypt(
                    encrypted, False
                )
                expire = 60 * 60 * 24 * 30
                cache.set(key, pickled, expire)

        keys = pickle.loads(cache.get(key))

        if name not in cls.__instances:
            cls.__instances[name] = Cipher(cls.__algorithm, cls.__mode, **keys)

        return cls.__instances[name]

    @classmethod
    def instances(cls):
        return cls.__instances


def persist_keys(cipher):
    pass
