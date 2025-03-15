class AccountOperationException(Exception):
    """Base exception for all account operation failures."""
    pass

class InsufficientFundsException(AccountOperationException):
    """Exception raised when a withdrawal would result in a negative balance."""
    pass

class NoSuchAccountException(AccountOperationException):
    """Exception raised when trying to operate on a non-existent account."""
    pass