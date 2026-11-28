from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Quote:
    symbol : str
    price : Decimal
    currency : str
    as_of : datetime
    source : str

@dataclass
class Holding:
    symbol : str
    position_id : int
    quantity_micros : int

@dataclass
class HoldingValue:
    symbol : str
    value : Decimal
    currency : str
    as_of : datetime
    source : str
