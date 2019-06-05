class Error(Exception):
    """Base Exception class."""

class BadRequestError(Error):
    """Something went wrong in the request."""