# utils.py

import time

def current_timestamp():
    return int(time.time())

def percentage_change(old, new):
    try:
        return ((new - old) / old) * 100
    except ZeroDivisionError:
        return 0

def format_usd(amount):
    return f"${amount:,.2f}"