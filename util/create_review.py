import datetime
import json
from urllib.parse import urlparse, parse_qs
from util.get_session import get_session

from util.database import review_collection
from util.database import user_collection
from util.response import Response
from util.read_files import read_files
from util.database import db
from datetime import datetime

def new_rev_path(request,handler):
    file_path = "public/new-review.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")


def next_id():

    last_review = review_collection.find_one(sort=[("id", -1)])

    if last_review:
        return last_review["id"] + 1

    return 1

def escape_html(txt):
    txt = txt.replace("&", "&amp;")
    txt = txt.replace("<", "&lt;")
    txt = txt.replace(">", "&gt;")
    return txt

def create_review(request, handler):
    user_collection = db["users"]

    auth_token = request.cookies.get("auth_token")

    if not auth_token:
        res = Response()
        res.set_status(401, "Unauthorized")
        handler.request.sendall(res.to_data())

    token = get_session(auth_token)
    user = user_collection.find_one({"auth_token": token})
    body = json.loads(request.body.decode('utf-8'))

    rating = body.get("rating")
    review_body = body.get("body")
    igdb_id = body.get("igdb_id")
    cover_url = body.get("cover_url")
    release_date = body.get("release_date")
    game_name = body.get("game_name")

    user = user_collection.find_one({"auth_token": token})
    if not user:
        res = Response()
        res.set_status(403, "Forbidden")
        res.text("user not authenticated")
        handler.request.sendall(res.to_data())

    existing_review = review_collection.find_one({
        "user_id": user["id"],
        "igdb_id": igdb_id
    })

    if existing_review:
        if existing_review["rating"] != rating:
            review_collection.update_one({
        "user_id": user["id"],
        "igdb_id": igdb_id
    }, {"$set": {"rating": rating}})

            res = Response()
            res.json({
                "success": True,
                "updated": True
            })
            handler.request.sendall(res.to_data())

        else:
            res = Response()
            res.set_status(403, "Forbidden")
            res.text("user already reviewed")
            handler.request.sendall(res.to_data())

    else:

        review_id = next_id()
        review = {
            "id": review_id,
            "user_id": user["id"],
            "igdb_id": igdb_id,
            "game_name": game_name,
            "cover_url": cover_url,
            "release_year": release_date,
            "body": escape_html(review_body),
            "rating": rating,
            "created_at": datetime.now().isoformat()
        }

        review_collection.insert_one(review)
        res = Response()
        res.json({
            "success": True
        })
        handler.request.sendall(res.to_data())





