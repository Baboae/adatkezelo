#functions/unix_to_datetime.py:

from datetime import datetime

def unix_to_dt(unix_time_ms: int) -> str:
    """
    Format a Unix timestamp (milliseconds) into "YY:MM:DD - hh:mm:ss".

    Args:
        unix_time_ms (int): Unix time in milliseconds.

    Returns:
        str: Formatted date string "YY:MM:DD - hh:mm:ss"
    """
    # ms -> seconds
    dt = datetime.utcfromtimestamp(unix_time_ms / 1000)

    # kétjegyű év, hónap, nap, óra, perc, másodperc
    return dt.strftime("%y.%m.%d - %H:%M:%S")
