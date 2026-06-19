
import uuid

import bcrypt

from util.auth import extract_credentials, validate_password
from util.response import Response
from util.request import Request
from util.read_files import read_files
from util.database import user_collection

def signup_path(request, handler):
    print("landing_path() called")
    file_path = "public/signup.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")

def signup_user(request, handler):
    username, password = extract_credentials(request)

    if not validate_password(password):
        res = Response()
        res.set_status(400, "Bad Request")
        res.text("Password must be at least 6 characters")
        handler.request.sendall(res.to_data())
        return

    if user_collection.find_one({"username": username}):
        res = Response()
        res.set_status(400, "Bad Request")
        res.text("Username already in use")
        handler.request.sendall(res.to_data())
        return

    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes, salt)

    user_id = str(uuid.uuid4())
    user_collection.insert_one(
        {
            "id": user_id,
            "username": username,
            "password": hashed,
            "auth_token": None,
            "nickname": username
        }
    )

    res = Response()
    res.set_status(201, "Created")
    res.text("Account created successfully")
    handler.request.sendall(res.to_data())

