import datetime
import json
from urllib.parse import urlparse, parse_qs
from util.database import comments_collection

from bson import ObjectId

from util.get_session import get_session

from util.database import review_collection
from util.database import user_collection
from util.response import Response
from util.read_files import read_files
from util.database import db
from util.igdb import search_igdb_games

def rev_page_path(request, handler):
    file_path = "public/review_page.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")

def view_rev(request, handler):

    body = json.loads(request.body.decode("utf-8"))
    review_id = body.get("id")


    if not review_id:
        res = Response()
        res.set_status(400, "Bad Request")
        res.text("Review ID is required")
        handler.request.sendall(res.to_data())

    review = review_collection.find_one({"id": review_id})

    if not review:
        res = Response()
        res.set_status(404, "Not Found")
        res.text("Review not found")
        handler.request.sendall(res.to_data())



    user = user_collection.find_one({"id": review["user_id"]})

    # Check if the current user has liked this review
    user_liked = False
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        token = get_session(auth_token)
        current_user = user_collection.find_one({"auth_token": token})
        if current_user:
            liked_by = review.get("liked_by", [])
            user_liked = current_user["id"] in liked_by

    # Get cover_url, fetch from IGDB if missing
    cover_url = review.get("cover_url")
    
    if not cover_url and review.get("igdb_id"):
        try:
            games = search_igdb_games(review["game_name"])
            if games:
                cover_url = games[0].get("cover", {}).get("url", "")
        except Exception as e:
            print(f"Error fetching cover from IGDB: {e}")

    # Normalize cover_url to proper format with https: and t_cover_big
    if cover_url:
        cover_url = cover_url.replace("t_thumb", "t_cover_big")
        if not cover_url.startswith("https://"):
            if cover_url.startswith("http://"):
                cover_url = cover_url.replace("http://", "https://", 1)
            elif cover_url.startswith("//"):
                cover_url = "https:" + cover_url
            else:
                cover_url = "https://" + cover_url

    entry = {
        "id": review["id"],
        "game_name": review["game_name"],
        "cover_url": cover_url or "",
        "release_year": review["release_year"],
        "rating": review["rating"],
        "body": review.get("body", ""),
        "likes": review.get("likes", 0),
        "user_liked": user_liked,
        "created_at": review["created_at"],
        "user": {
            "username": user["username"] if user else "Unknown",
            "id": review["user_id"]
        }
    }

    res = Response()
    res.json(entry)
    handler.request.sendall(res.to_data())


def like_review(request, handler):

    path_parts = request.path.split("/")
    review_id = int(path_parts[3])
 

    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        res = Response()
        res.set_status(401, "Unauthorized")
        res.text("No auth token")
        handler.request.sendall(res.to_data())


    token = get_session(auth_token)
    user = user_collection.find_one({"auth_token": token})
    if not user:
        res = Response()
        res.set_status(403, "Forbidden")
        res.text("User not authenticated")
        handler.request.sendall(res.to_data())
 

    review = review_collection.find_one({"id": review_id})
    if not review:
        res = Response()
        res.set_status(404, "Not Found")
        res.text("Review not found")
        handler.request.sendall(res.to_data())


    # Toggle like
    user_id = user["id"]
    liked_by = review.get("liked_by", [])
    current_likes = review.get("likes", 0)

    if user_id in liked_by:
        liked_by.remove(user_id)
        current_likes = max(0, current_likes - 1)
    else:
        liked_by.append(user_id)
        current_likes += 1

    review_collection.update_one(
        {"id": review_id},
        {"$set": {"liked_by": liked_by, "likes": current_likes}}
    )

    res = Response()
    res.json({"likes": current_likes, "liked": user_id in liked_by})
    handler.request.sendall(res.to_data())

