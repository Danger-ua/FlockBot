from simplecrypto import decrypt, encrypt
from base64 import b64encode, b64decode
import secrets


def get_random_token(size=16):
    return secrets.token_hex(size)


def encode(plain_str):
    cipher = encrypt(plain_str, key)
    cipher = bytes(cipher, 'utf8')
    encoded_str = b64encode(cipher)
    print(encoded_str)
    return encoded_str


def decode(enc_str):
    cipher = b64decode(enc_str)
    plain_str = decrypt(cipher, key)
    dec_str = bytes(plain_str).decode('utf8')
    print(dec_str)
    return dec_str


def get_key():
    f = open('/etc/machine-id', 'r')
    mid = f.read()[:-1]
    f.close()
    return mid


key = get_key()
