from util.response import Response
from util.request import Request
from util.read_files import read_files

def landing_path(request, handler):
    print("landing_path() called")
    file_path = "public/index.html"
    content = read_files(file_path)
    res = Response()
    res.bytes(content)
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    print("Sending response:", res.to_data())
    handler.request.sendall(res.to_data())
    print("Response sent")
