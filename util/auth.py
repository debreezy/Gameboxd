from util.response import Response
import json

def decode_percentencoding(v):
    string = ""
    i = 0
    while i < len(v):
        if v[i] == '%' and i+2 < len(v):
            value = v[i+1:i+3]
            string += chr(int(value, 16))
            i += 3
        else:
            string += v[i]
            i += 1
    return string

def extract_credentials(request):
    body = request.body.decode('utf-8')

    credentials = {}
    creds = body.split('&')

    for pair in creds:
        key,value = pair.split('=')

        if key == 'username':
                username = value
        elif key == 'password':
            password = decode_percentencoding(value)

    return [username, password]

def validate_password(password):

    special_characters = "!@#$%^&()-_ ="
    allowed_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") | set(special_characters)

    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.islower() for char in password):
       return False
    if not any(char in special_characters for char in password):
       return False
    if not all(char in allowed_characters for char in password):
        return False

    return True