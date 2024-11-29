import base64


def convert_to_dict(obj, skip_empty=False):
    """
    Convert DataClasses to Python Dictionary
    """
    return {
        key: value
        for key, value in obj.__dict__.items()
        if not (skip_empty and value is None)
    }


def encode_by_base64(string: str) -> str:
    """
    Encodes string to byte and converts into encoded string
    """
    encoded_token = base64.b64encode(string.encode("utf-8"))
    encoded_token = str(encoded_token).split("'")[1]
    return encoded_token


def decode_by_base64(string: str) -> str:
    """
    Decodes string type encoded token to string
    """
    encoded_token = bytes(string, "utf-8")
    decoded_token = base64.b64decode(encoded_token).decode("utf-8")
    return decoded_token
