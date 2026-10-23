from repository.accounts import list_accounts
from portfolio.quantity import convert_shares_to_millionths
from repository.holdings import insert_opening_position_in_database

def get_holdings():
    return []

def get_accounts():
    return list_accounts()

def open_holding(account_id : int, ticker : str, quantity : str):
    # convert quantity to micros, if sucessfull send it off to the repostitory
    quantity_micros = convert_shares_to_millionths(quantity)
    position_id = insert_opening_position_in_database(account_id, ticker, quantity_micros)
    return position_id