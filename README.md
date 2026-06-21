







backend routes to wire for game page
# GET /api/games/popular
# return up to 50 popular games from IGDB
data = 'fields name,cover.url,first_release_date; sort popularity desc; limit 50;'


for filter
# GET /api/games/search?q=query
# return search results from IGDB
data = f'search "{query}"; fields name,cover.url,first_release_date; limit 50;'

create search games file
return games based off keyword input by user
using query strings
GET request