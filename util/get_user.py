from util.response import Response
from util.database import db
from util.get_session import get_session
import json

def get_user(request,handler):
   user_collection = db["users"]

   auth_token = request.cookies.get("auth_token")

   if not auth_token:
       res = Response()
       res.set_status(401, "Unauthorized")
       handler.request.sendall(res.to_data())

   token = get_session(auth_token)
   user = user_collection.find_one({"auth_token": token})

   print(user["username"])

   user_data = {
       "username": user["username"],
       "id": user["id"]
   }

   res = Response()
   res.json(user_data)
   handler.request.sendall(res.to_data())