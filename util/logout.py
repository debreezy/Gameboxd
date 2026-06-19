import uuid

import bcrypt

from util.auth import extract_credentials, validate_password
from util.database import db
from util.response import Response

import hashlib


def logout_view(request, handler):
    user_collection = db["users"]
    token_cookie = request.cookies.get("auth_token")

    if not token_cookie:
        res = Response()
        res.set_status(403, "Forbidden")
        res.text("Nice try bud")
        handler.request.sendall(res.to_data())

    token = token_cookie.split(";")[0].strip()
    token_bytes = token.encode("utf-8")

    hashed_token = hashlib.sha256(token_bytes).hexdigest()
    user = user_collection.find_one({"auth_token": hashed_token})
    if not user:
        res = Response()
        res.set_status(403, "Forbidden")
        res.text("Nice try bud")
        handler.request.sendall(res.to_data())

    id = user["id"]
    user_collection.update_one({"id": id}, {"$unset": {"auth_token": ""}})

    res = Response()
    res.set_status(302, "Found")
    res.headers({"Location": "/"})
    res.cookies({"auth_token": f"{token};Max-Age=0"})
    handler.request.sendall(res.to_data())
