
import requests
import os

def get_igdb_token():
    token_res = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id":     os.getenv("TWITCH_CLIENT_ID"),
            "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
            "grant_type":    "client_credentials"
        }
    )
    token = token_res.json()["access_token"]
    return token

def search_igdb_games(query):
    token = get_igdb_token()

    res = requests.post(
        "https://api.igdb.com/v4/games",
        headers={
            "Client-ID":     os.getenv("TWITCH_CLIENT_ID"),
            "Authorization": f"Bearer {token}"
        },
        data=f'search "{query}"; fields name,cover.url,first_release_date,summary; limit 10;'
    )
    return res.json()