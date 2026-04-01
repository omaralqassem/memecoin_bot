# risk.py

MAX_RISK_PER_TRADE = 0.01   # 1%
MAX_DAILY_LOSS = 0.05       # 5%
MAX_OPEN_TRADES = 3

RISK_REWARD_RATIO = 2       # TP = 2x SL

def calculate_position_size(balance, entry, stop_loss):
    risk_amount = balance * MAX_RISK_PER_TRADE
    loss_per_token = abs(entry - stop_loss)

    if loss_per_token == 0:
        return 0

    position_size = risk_amount / loss_per_token
    return position_size


def calculate_levels(entry_price):
    stop_loss = entry_price * 0.90   # -10%
    take_profit = entry_price * 1.20 # +20%
    return stop_loss, take_profit