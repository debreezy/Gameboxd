import json


class Request:

    def __init__(self, request: bytes):

        header, bod = request.split(b"\r\n\r\n", 1)

        print("before decode:", header)
        header = header.decode('utf-8')

        request_line, header_lines = header.split("\r\n", 1)
        lines = header_lines.split("\r\n")

        print("request line:", request_line)
        print("header line:", header_lines)

        request_line_parts = request_line.split(" ")
        # print(request_line_parts[0])
        # print(request_line_parts[1])
        # print(request_line_parts[2])

        cookies_dict = {}
        header_dict = {}
        for line in lines:
            key, value = line.split(":", 1)
            header_dict[key] = value.strip()
            if key == "Cookie":
                cookie_pairs = value.split(";")
                for pair in cookie_pairs:
                    cookie_key, cookie_value = pair.strip().split("=", 1)
                    cookies_dict[cookie_key] = cookie_value

        # print(lines)
        print(header_dict)

        self.body = bod
        self.method = request_line_parts[0]
        self.path = request_line_parts[1]
        self.http_version = request_line_parts[2]
        self.headers = header_dict
        self.cookies = cookies_dict


def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert request.path == "/"
    assert request.http_version == "HTTP/1.1"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"
    assert request.headers["Connection"] == "keep-alive"
    assert request.body == b""


def test2():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nCookie: sessionid=abc123; theme=light\r\n\r\n')
    assert request.method == "GET"
    assert "Cookie" in request.headers
    assert request.headers["Cookie"] == "sessionid=abc123; theme=light"
    assert isinstance(request.cookies, dict)
    assert request.cookies.get("sessionid") == "abc123"
    assert request.cookies.get("theme") == "light"


def test3():
    json_data = {"username": "testuser", "password": "testpass"}
    json_body = json.dumps(json_data).encode('utf-8')
    content_length = len(json_body)

    header_str = (
        'POST /login HTTP/1.1\r\n'
        'Host: localhost:8080\r\n'
        f'Content-Length: {content_length}\r\n'
        'Content-Type: application/json\r\n'
        '\r\n'
    )
    request_bytes = header_str.encode('utf-8') + json_body

    request = Request(request_bytes)
    assert request.method == "POST"
    assert request.path == "/login"
    assert request.http_version == "HTTP/1.1"
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["Content-Length"] == str(content_length)
    assert request.body == json_body

    parsed_json = json.loads(request.body.decode('utf-8'))
    assert parsed_json["username"] == "testuser"
    assert parsed_json["password"] == "testpass"


if __name__ == '__main__':
    test1()
    test2()
    test3()
    print("All tests passed.")
