import base64


def convert_to_base64(raw_string):
    encoded_data = base64.b64encode(raw_string.encode())
    
    return encoded_data.decode("utf-8")


def base64_to_string(encoded_data):
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data.decode("utf-8")
