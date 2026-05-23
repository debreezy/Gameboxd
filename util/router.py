from util.response import Response
from util.request import Request


class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):

        self.routes.append(
            {
                "method": method,
                "path": path,
                "action": action,
                "exact_path": exact_path
            }
        )

    def route_request(self, request, handler):
        for route in self.routes:
            if request.method == route["method"]:
                print("Routing to:", route["path"])
                if route["exact_path"]:  # if bool was true
                    if request.path == route["path"]:
                        route["action"](request, handler)  # calls function
                        return

                else:
                    if request.path.startswith(route["path"]):
                        route["action"](request, handler)
                        return

        # if no path matches return 404
        res = Response()
        res.set_status("404", "Not Found")
        res.text("no page bro")
        handler.request.sendall(res.to_data())


