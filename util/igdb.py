
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
    
    if token_res.status_code != 200:
        print(f"Error: Token request failed with status {token_res.status_code}")
        print(f"Response: {token_res.text}")
        raise Exception(f"Failed to get IGDB token: {token_res.text}")
    
    response_data = token_res.json()
    if "access_token" not in response_data:
        print(f"Error: No access_token in response")
        print(f"Response: {response_data}")
        raise KeyError(f"access_token not in response. Got: {response_data}")

    print(response_data)
    
    token = response_data["access_token"]
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