def convert_shares_to_millionths(shares) -> int:
    # we define -1 to be an unsucessful conversion
    if shares == None or not isinstance(shares, str):
            return -1
    parts = shares.split(".")
    # cases that don't depend on there being a second element in the parts array
    if (len(parts) > 2 or not parts[0].isdecimal() or int(parts[0]) < 0):
        return -1
    
    # cases that do depend on there being a second element
    if (len(parts) == 2):
        if (not parts[1].isdecimal() or len(parts[1]) > 6):
            return -1
        
    # guards passed, valid value
    millionths = 1000000 * int(parts[0])
    if (len(parts) == 2):
        millionths += int(parts[1]) * (10 ** (6 - len(parts[1])))
    if (millionths == 0):
        return -1
    
    return millionths