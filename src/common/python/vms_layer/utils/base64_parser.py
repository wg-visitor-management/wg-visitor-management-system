import base64


def convert_to_base64(raw_string):
    """Converts a string to base64 encoded string and returns it."""
    encoded_data = base64.b64encode(raw_string.encode())    
    return encoded_data.decode("utf-8")


def base64_to_string(encoded_data):
    """Converts a base64 encoded string to a string and returns it."""
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data.decode("utf-8")
