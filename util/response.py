import json


class Response:
    def __init__(self):
        self.body = b""
        self.status_code = "200"
        self.status_message = "OK"
        self.header_data = {
                            "Content-Type": "text/plain; charset=utf-8",
                            "X-Content-Type-Options": "nosniff"
                            }
        self.cookie_data = {}
        pass

    def set_status(self, code, text):
        self.status_code = str(code)
        self.status_message = text
        return self

    def headers(self, headers):
        for key, value in headers.items():
            self.header_data[key] = value
        return self

    def cookies(self, cookies):
        for key, value in cookies.items():
            self.cookie_data[key] = value
        return self

    def bytes(self, data):
        self.body += data
        return self

    def text(self, data):
        self.body += data.encode('utf-8')
        return self

    def json(self, data):
        json_data = json.dumps(data)
        self.header_data["Content-Type"] = "application/json"
        self.body = json_data.encode('utf-8')
        return self

    def to_data(self):
        response = f"HTTP/1.1 {self.status_code} {self.status_message}\r\n"
        for key,value in self.header_data.items():
            response += f"{key}: {value}\r\n"
        response += f"Content-Length: {len(self.body)}\r\n"
        if self.cookie_data != {}:
            for key,value in self.cookie_data.items():
                response += f"Set-Cookie: {key}={value}\r\n"
        response += "\r\n"
        response = response.encode('utf-8') + self.body

        return response


def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()
    if actual != expected:
        print("Expected:", expected)
        print("Actual:", actual)
        raise AssertionError("test1 failed")
    assert actual == expected

def test2():
    res = Response()
    json_payload = {"message": "Hello, World!"}
    res.json(json_payload)
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 28\r\n\r\n{"message": "Hello, World!"}'
    actual = res.to_data()
    if actual != expected:
        print("Expected:", expected)
        print("Actual:", actual)
        raise AssertionError("test2 failed")
    assert actual == expected

def test3():
    res = Response()
    res.set_status("404", "Not Found")
    res.headers({"Custom-Header": "CustomValue"})
    res.cookies({"sessionid": "abc123"})
    res.text("Page not found")
    expected = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nCustom-Header: CustomValue\r\nContent-Length: 14\r\nSet-Cookie: sessionid=abc123\r\n\r\nPage not found'
    actual = res.to_data()

    if actual != expected:
        print("Expected:", expected)
        print("Actual:", actual)
        raise AssertionError("test3 failed")

    assert actual == expected

def test4():
    res = Response()
    actual = res.to_data()
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n'

    if actual != expected:
        print("Expected:", expected)
        print("Actual:", actual)
        raise AssertionError("test4 failed")

    assert actual == expected


def test5():
    res = Response()
    actual = res.to_data()
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n'
    if actual != expected:
        print("Expected:", expected)
        print("Actual:", actual)
        raise AssertionError("test5 failed")
    assert actual == expected


def test6():
    res = Response()
    res.text("Hello ").text("World").text("!")
    actual = res.to_data()
    assert b"Hello World!" in actual
    assert b"Content-Length: 12" in actual


def test7():
    res = Response()
    res.bytes(b"Binary ").bytes(b"Data").bytes(b"!")
    actual = res.to_data()
    assert b"Binary Data!" in actual
    assert b"Content-Length: 12" in actual


def test8():
    res = Response()
    res.text("Text ").bytes(b"and ").text("bytes")
    actual = res.to_data()
    assert b"Text and bytes" in actual
    assert b"Content-Length: 14" in actual


def test9():
    res = Response()
    res.text("🌍")
    actual = res.to_data()
    assert "🌍".encode('utf-8') in actual
    assert b"Content-Length: 4" in actual


def test10():
    res = Response()
    res.json({})
    actual = res.to_data()
    assert b"{}" in actual
    assert b"Content-Length: 2" in actual
    assert b"application/json" in actual


def test11():
    res = Response()
    json_payload = {
        "user": {
            "name": "Rahul",
            "age": 22,
            "hobbies": ["reading", "coding"]
        }
    }
    res.json(json_payload)
    actual = res.to_data()
    assert b"application/json" in actual
    assert b"Rahul" in actual
    assert b"hobbies" in actual
    assert b"reading" in actual
    assert b"coding" in actual


def test12():
    res = Response()
    res.json([1, 2, 3, 4, 5])
    actual = res.to_data()
    assert b"[1, 2, 3, 4, 5]" in actual
    assert b"application/json" in actual


def test13():
    res = Response()
    res.cookies({"session": "abc123", "user": "rahul", "visits": "4"})
    res.text("test")
    actual = res.to_data()
    print(actual)
    assert b"Set-Cookie: session=abc123" in actual
    assert b"Set-Cookie: user=rahul" in actual
    assert b"Set-Cookie: visits=4" in actual


def test14():
    res = Response()
    res.headers({"Content-Type": "text/html; charset=utf-8"})
    res.text("test")
    actual = res.to_data()

    assert b"Content-Type: text/html; charset=utf-8" in actual
    assert b"Content-Type: text/plain; charset=utf-8" not in actual

    header_section = actual.split(b'\r\n\r\n')[0]
    content_type_lines = [line for line in header_section.split(b'\r\n') if line.startswith(b'Content-Type:')]
    assert len(content_type_lines) == 1, f"Expected 1 Content-Type header, found {len(content_type_lines)}"


def test15():
    res = (Response()
           .set_status("201", "Created")
           .headers({"Location": "/resource/123"})
           .cookies({"created": "true"})
           .text("Resource created"))
    actual = res.to_data()
    assert b"201 Created" in actual
    assert b"Location: /resource/123" in actual
    assert b"Set-Cookie: created=true" in actual
    assert b"Resource created" in actual



def test16():
    res = Response()
    res.cookies({"empty": ""})
    res.text("test")
    actual = res.to_data()
    assert b"Set-Cookie: empty=" in actual


def test17():
    res = Response()
    res.headers({"X-Custom": "value-with-dashes_and_underscores"})
    res.text("test")
    actual = res.to_data()
    assert b"X-Custom: value-with-dashes_and_underscores" in actual


def test18():
    res = Response()
    res.json({"message": "Line1\nLine2\tTabbed\"Quoted\\"})
    actual = res.to_data()
    assert b"application/json" in actual
    # JSON should escape these characters
    assert b"\\n" in actual or b"\n" in actual
    assert b"\\t" in actual or b"\t" in actual


def test19():
    res = Response()
    large_text = "A" * 10000
    res.text(large_text)
    actual = res.to_data()
    assert b"Content-Length: 10000" in actual
    assert large_text.encode('utf-8') in actual

def test20():
    res = Response()
    binary_data = bytes(range(256))
    res.bytes(binary_data)
    actual = res.to_data()
    assert binary_data in actual
    assert b"Content-Length: 256" in actual



def test21():
    res = Response()
    res.json({"value": None})
    actual = res.to_data()
    assert b'"value": null' in actual


def test22():
    res = Response()
    res.text("test")
    actual = res.to_data()
    assert b"Set-Cookie" not in actual


def test23():
    res = Response()
    res.headers({"Content-Type": "text/html"})
    res.json({"test": "data"})
    actual = res.to_data()
    assert b"application/json" in actual
    assert b"text/html" not in actual

def test24():
    res = Response()
    res.cookies({"session_id": "abc123; Max-Age=3600"})
    res.text("test")

    actual = res.to_data()
    assert b"Set-Cookie: session_id=abc123; Max-Age=3600" in actual




if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
    test9()
    test10()
    test11()
    test12()
    test13()
    test14()
    test15()
    test16()
    test17()
    test18()
    test19()
    test20()
    test21()
    test22()
    test23()
    test24()
    print("All tests passed!")



