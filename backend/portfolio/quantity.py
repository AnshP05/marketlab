from portfolio.errors import InvalidQuantityError


def convert_shares_to_millionths(shares) -> int:
    # Invalid input raises InvalidQuantityError; valid input returns millionths.
    if shares == None or not isinstance(shares, str):
        raise InvalidQuantityError("Quantity must be a string, for example '2.25'.")
    parts = shares.split(".")
    # Check the overall format before checking the fractional part.
    if (len(parts) > 2):
        raise InvalidQuantityError("Quantity must contain at most one decimal point.")
    if (not parts[0].isdecimal()):
        raise InvalidQuantityError(
            "Quantity must begin with one or more digits. "
            "Signs, letters, and spaces are not allowed."
        )
    
    # cases that do depend on there being a second element
    if (len(parts) == 2):
        if (not parts[1].isdecimal()):
            raise InvalidQuantityError(
                "Quantity must contain only digits after the decimal point, "
                "with at least one digit, for example '2.25'."
            )
        if (len(parts[1]) > 6):
            raise InvalidQuantityError(
                "Quantity must have no more than 6 digits after the decimal point."
            )
        
    # guards passed, valid value
    millionths = 1000000 * int(parts[0])
    if (len(parts) == 2):
        millionths += int(parts[1]) * (10 ** (6 - len(parts[1])))
    if (millionths == 0):
        raise InvalidQuantityError("Quantity must be greater than zero.")
    
    return millionths
