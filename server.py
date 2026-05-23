import socketserver

from util.request import Request
from util.response import Response
from util.router import Router

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()

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