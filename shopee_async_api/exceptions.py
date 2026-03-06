class ShopeeAPIError(Exception):
    """Base exception for all Shopee API errors."""
    pass

class ShopeeAuthError(ShopeeAPIError):
    """Raised when there is an authentication or signature error (e.g. 10020)."""
    pass

class ShopeeRateLimitError(ShopeeAPIError):
    """Raised when the rate limit is exceeded (e.g. 10030)."""
    pass

class ShopeeBusinessError(ShopeeAPIError):
    """Raised on general business errors (e.g. 11000)."""
    pass

class ShopeeParamsError(ShopeeAPIError):
    """Raised when parameters are invalid (e.g. 11001)."""
    pass

class ShopeeBindAccountError(ShopeeAPIError):
    """Raised when there is an account binding error (e.g. 11002)."""
    pass

class ShopeeAccessDeniedError(ShopeeAPIError):
    """Raised when access is denied or account is frozen/blocked (e.g. 10031 - 10035)."""
    pass

def handle_api_error(error_code: int, error_msg: str):
    """Maps custom Shopee API GraphQL errors to Python exceptions."""
    if error_code == 10020:
        raise ShopeeAuthError(f"Auth Error [{error_code}]: {error_msg}")
    elif error_code == 10030:
        raise ShopeeRateLimitError(f"Rate Limit Exceeded [{error_code}]: {error_msg}")
    elif error_code in (10031, 10032, 10033, 10034, 10035):
        raise ShopeeAccessDeniedError(f"Access Denied [{error_code}]: {error_msg}")
    elif error_code == 11000:
        raise ShopeeBusinessError(f"Business Error [{error_code}]: {error_msg}")
    elif error_code == 11001:
        raise ShopeeParamsError(f"Params Error [{error_code}]: {error_msg}")
    elif error_code == 11002:
        raise ShopeeBindAccountError(f"Bind Account Error [{error_code}]: {error_msg}")
    elif error_code != 0:
        raise ShopeeAPIError(f"Unknown API Error [{error_code}]: {error_msg}")
