

class ApplicationBaseError(Exception):
    """Base class for other exceptions"""


class UserError(ApplicationBaseError):
    """Base class for user errors"""


class SingUpExpiredError(UserError):
    """Lifetime token sign up is expired """

