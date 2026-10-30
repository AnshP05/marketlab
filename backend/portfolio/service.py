from repository.accounts import list_accounts
from portfolio.quantity import convert_shares_to_millionths, convert_millionths_to_shares
from repository.holdings import insert_opening_position_in_database, list_opening_positions

def get_holdings():
    return []

def get_accounts():
    return list_accounts()

def open_holding(account_id : int, ticker : str, quantity : str):
    # convert quantity to micros, if sucessfull send it off to the repostitory
    quantity_micros = convert_shares_to_millionths(quantity)
    position_id = insert_opening_position_in_database(account_id, ticker, quantity_micros)
    return position_id

def get_opening_positions():
    opening_positions_micros = list_opening_positions()
    opening_positions = []
    for position_id, account_id, account_name, symbol, quantity_micros in opening_positions_micros:
        opening_positions.append({
                                    "position_id": position_id, 
                                    "account_id":account_id, 
                                    "account_name": account_name, 
                                    "symbol": symbol, 
                                    "shares": convert_millionths_to_shares(quantity_micros)
                                })
    return opening_positions