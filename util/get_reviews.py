import json
from urllib.parse import urlparse, parse_qs
from util.get_session import get_session

from util.database import review_collection
from util.database import user_collection
from util.read_files import read_files
from util.response import Response
from util.get_session import get_session
from util.database import db
from datetime import datetime, timedelta


def journal_path(request, handler):
    file_path = "public/journal.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")

def all_activity_path(request, handler):
    file_path = "public/all-activity.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")

def recent_activity(request, handler):
  
    parsed = urlparse(request.path)
    params = parse_qs(parsed.query)
    get_all = params.get("all", [None])[0]
    
    limit = None if get_all else 4

    query = review_collection.find().sort("created_at", -1)
    if limit is not None:
        query = query.limit(limit)
    reviews = list(query)
    entries = []

    for review in reviews:
        user = user_collection.find_one({
            "id": review["user_id"]
        })

        entries.append({
            "id": review["id"],
            "game": {
                "title": review["game_name"],
                "cover_url": review["cover_url"]
            },
            "user": {
                "username": user["username"] if user else "Unknown"
            },
            "rating": review.get("rating", 0),
            "body": review.get("body", "")[:100],
            "played_at": review.get("created_at")
        })

    res = Response()
    res.json(entries)
    handler.request.sendall(res.to_data())


def get_reviews(request, handler):
    user_collection = db["users"]

    auth_token = request.cookies.get("auth_token")

    if not auth_token:
        res = Response()
        res.set_status(401, "Unauthorized")
        handler.request.sendall(res.to_data())

    token = get_session(auth_token)
    user = user_collection.find_one({"auth_token": token})
    user_id = user["id"]

    reviews = list(review_collection.find({"user_id": user_id}))
    body = []
    for rev in reviews:
        body.append({
            "id": rev["igdb_id"],
            "game": {
                "title": rev["game_name"],
                "cover_url": rev["cover_url"],
                "release_year": rev["release_year"],
            },
            "rating": rev["rating"],
            "body": rev["body"],
            "created_at": rev["created_at"]
        })

    res = Response()
    res.json(body)
    handler.request.sendall(res.to_data())


