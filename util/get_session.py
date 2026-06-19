import hashlib

from util.database import db

def get_session(token_cookie):

    token = token_cookie.split(";")[0].strip()
    token_bytes = token.encode("utf-8")

    hashed_token = hashlib.sha256(token_bytes).hexdigest()
    return hashed_token