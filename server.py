import socketserver

from util.request import Request
from util.response import Response
from util.router import Router
from util.index import landing_path
from util.login import login_path, login_user
from util.signup import signup_path, signup_user
from util.get_user import get_user
from util.logout import logout_view
from util.home import home_path
from util.get_games import games_path
from util.get_games import search_games
from util.get_games import popular_games
from util.get_reviews import journal_path
from util.get_reviews import get_reviews
from util.create_review import create_review
from util.create_review import new_rev_path
from util.get_reviews import recent_activity
class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route('GET', '/', landing_path, True)
        self.router.add_route('GET', '/login', login_path, True)
        self.router.add_route('GET', '/signup', signup_path, True)
        self.router.add_route('POST', '/register', signup_user, False)
        self.router.add_route('POST', '/login', login_user, False)
        self.router.add_route("GET", "/api/users/@me", get_user, False)
        self.router.add_route("GET", "/logout", logout_view, False)
        self.router.add_route("GET", "/home", home_path, True)
        self.router.add_route("GET", "/games", games_path, True)
        self.router.add_route("GET", "/api/games/search", search_games, False)
        self.router.add_route("GET", "/api/games/popular", popular_games, False)
        self.router.add_route("GET", "/journal", journal_path, True)
        self.router.add_route("GET", "/new-review", new_rev_path, True)
        self.router.add_route("GET", "/api/journal", get_reviews, False)
        self.router.add_route("POST", "/api/reviews", create_review, False)
        self.router.add_route("GET", "/api/activity/recent",recent_activity , True)

        super().__init__(request, client_address, server)

        #add paths

    def handle(self):
        print("===== HANDLE CALLED =====", flush=True)
        print("About to receive data", flush=True)
        received_data = self.request.recv(2048)
        print(self.client_address, flush=True)
        print("--- received data ---", flush=True)
        print(received_data, flush=True)
        print("--- end of data ---\n\n", flush=True)
        print("About to create Request", flush=True)
        request = Request(received_data)
        print("Request created, about to route", flush=True)

        self.router.route_request(request, self)
        print("Request routed successfully", flush=True)

def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port" + str(port))
    server.serve_forever()

if __name__ == "__main__":
    main()