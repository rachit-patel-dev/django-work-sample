import re


def validate_email_by_regex(email: str) -> bool:
    """
    Email Validation using RegEx
    returns : bool
    """
    email_pattern = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"

    result = re.match(email_pattern, email)

    return True if result else False


def validate_password_by_regex(password: str) -> bool:
    """
    Password Validation using RegEx
    returns : bool

    Password Criteria :
    1. At least one digit[0 - 9]
    2. At least one lowercase character[a - z]
    3. At least one uppercase character[A - Z]
    4. At least one special character[*.!@#$%^&(){}[]:;<>,.?/~_+-=|\]
    5. At least 8 characters in length, but no more than 32.
    """

    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[*.!@#$%^&(){}[\]:;<>,.?/~_+\-=|\\])[A-Za-z\d*.!@#$%^&(){}[\]:;<>,.?/~_+\-=|\\]{8,32}$"

    result = re.match(password_pattern, password)
    return True if result else False
