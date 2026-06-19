from util.response import Response
from util.request import Request
from util.read_files import read_files

import uuid
import hashlib
import bcrypt
from util.auth import extract_credentials, validate_password
from util.database import user_collection

def login_path(request, handler):
    print("landing_path() called")
    file_path = "public/login.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")

def login_user(request, handler):
    username, password = extract_credentials(request)
    print(f"Login attempt: username={username}", flush=True)
    
    user = user_collection.find_one({"username": username})
    print(f"User found: {user is not None}", flush=True)
    
    if not user:
        print(f"User '{username}' not found in database", flush=True)
        res = Response()
        res.set_status(400, "User not found")
        res.text("Username not found")
        handler.request.sendall(res.to_data())
        return
    
    print(f"User password field type: {type(user.get('password'))}", flush=True)
    
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        res = Response()
        res.set_status(400, "Incorrect password")
        res.text("Incorrect password")
        handler.request.sendall(res.to_data())
        return

    auth_token = str(uuid.uuid4())
    auth_token_bytes = auth_token.encode("utf-8")
    hashed_token = hashlib.sha256(auth_token_bytes).hexdigest()
    user_id = user["id"]

    user_collection.update_one({"id": user_id}, {"$set": {"auth_token": hashed_token}})

    res = Response()
    res.text("Login successful")
    res.cookies({"auth_token": f"{auth_token}; HttpOnly; Max-Age=3600"})
    handler.request.sendall(res.to_data())



