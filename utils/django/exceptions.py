from dataclasses import dataclass


# =================================================================================================
# USER EXCEPTIONS
# =================================================================================================
class UserException(Exception):
    """
    Base class for User exceptions
    """

    pass


@dataclass(frozen=True)
class UserDoesNotExist(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class UserDoesNotVerified(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class UserAlreadyExist(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class InvalidCredentialsException(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class ValidationException(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class ForgotPasswordInstanceDoesNotExist(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class ForgotPasswordException(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class ForgotPasswordLinkExpired(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class SendgridEmailException(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)


@dataclass(frozen=True)
class InvalidParameterException(UserException):
    message: str
    item: dict

    def __str__(self):
        return "{}: {}".format(self.message, self.item)
