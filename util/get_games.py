# api/games/search_games.py

import json
from urllib.parse import urlparse, parse_qs
from util.igdb import get_igdb_token
from util.igdb import search_igdb_games
from util.response import Response
from util.read_files import read_files
from util.database import review_collection
import requests
import os
from datetime import datetime, timedelta
from util.database import user_collection



def games_path(request,handler):
    file_path = "public/game-page.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")


def search_games(request, handler):
    res = Response()
    res.headers({"Content-Type": "application/json"})

    parsed = urlparse(request.path)
    params = parse_qs(parsed.query)
    query  = params.get("q", [None])[0]

    if not query or not query.strip():
        res.set_status(400, "Bad Request")
        res.text(json.dumps({"error": "Missing ?q= parameter"}))
        handler.request.sendall(res.to_data())
        return

    games = search_igdb_games(query.strip())

    res.text(json.dumps(games))
    handler.request.sendall(res.to_data())

def popular_games(request, handler):
    token = get_igdb_token()
    client_id = os.getenv("TWITCH_CLIENT_ID")

    igdb_res = requests.post(
        "https://api.igdb.com/v4/games",
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {token}"
        },
        data="fields name,cover.url,first_release_date; where rating_count > 500; sort popularity desc; limit 100;"
    )

    res = Response()
    res.headers({"Content-Type": "application/json"})
    res.text(json.dumps(igdb_res.json()))
    handler.request.sendall(res.to_data())


def trending_games(request, handler):
        
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_iso = week_ago.isoformat()
    
    # Get reviews from the last 7 days (comparing ISO strings)
    reviews = list(
        review_collection.find({
            "created_at": {"$gte": week_ago_iso}
        }).sort("created_at", -1)
    )
    
    print(f"Found {len(reviews)} reviews from past week")
    
    game_counts = {}
    games_info = {}
    
    for review in reviews:
        game_id = review.get("igdb_id")
        if not game_id:
            continue
        
        if game_id not in game_counts:
            game_counts[game_id] = 0
            games_info[game_id] = {
                "id": game_id,
                "title": review.get("game_name"),
                "cover_url": review.get("cover_url")
            }
        
        game_counts[game_id] += 1
    
    sorted_games = sorted(
        games_info.items(),
        key=lambda x: game_counts[x[0]],
        reverse=True
    )[:4]
    
    trending = [game_data for game_id, game_data in sorted_games]
    
    print(f"Returning {len(trending)} trending games")
    
    res = Response()
    res.headers({"Content-Type": "application/json"})
    res.text(json.dumps(trending))
    handler.request.sendall(res.to_data())


def popular_reviews(request, handler):

    reviews = list(
        review_collection.find().sort("likes", -1).limit(4)
    )
    
    result = []
    for review in reviews:
        user = user_collection.find_one({"id": review.get("user_id")})
        
        # Format cover_url properly
        cover_url = review.get("cover_url", "")
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
            "game": {
                "title": review.get("game_name"),
                "cover_url": cover_url,
                "release_year": review.get("release_year")
            },
            "user": {
                "username": user["username"] if user else "Unknown"
            },
            "rating": review.get("rating"),
            "body": review.get("body", ""),
            "likes": review.get("likes", 0),
            "created_at": review.get("created_at")
        }
        result.append(entry)
    
    res = Response()
    res.headers({"Content-Type": "application/json"})
    res.text(json.dumps(result))
    handler.request.sendall(res.to_data())

