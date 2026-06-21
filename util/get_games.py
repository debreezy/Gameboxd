# api/games/search_games.py

import json
from urllib.parse import urlparse, parse_qs
from util.igdb import get_igdb_token
from util.igdb import search_igdb_games
from util.response import Response
from util.read_files import read_files
import requests
import os



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

    igdb_res = requests.post(
        "https://api.igdb.com/v4/games",
        headers={
            "Client-ID": os.getenv("TWITCH_CLIENT_ID"),
            "Authorization": f"Bearer {token}"
        },
        data="fields name,cover.url,first_release_date; where rating_count > 500; sort popularity desc; limit 100;"
    )

    res = Response()
    res.headers({"Content-Type": "application/json"})
    res.text(json.dumps(igdb_res.json()))
    handler.request.sendall(res.to_data())
