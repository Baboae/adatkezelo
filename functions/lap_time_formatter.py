def format_lap_time(unix_time_ms: int) -> str:
    """
    Format a lap time given in Unix-style milliseconds into perc:mp:tizedmp form.

    Args:
        unix_time_ms (int): Lap time in milliseconds.

    Returns:
        str: Formatted time string "minutes:seconds:milliseconds"
    """
    minutes = unix_time_ms // 60000
    seconds = (unix_time_ms % 60000) // 1000
    milliseconds = unix_time_ms % 1000

    # mindig 3 jegyű milliszekundum
    return f"{minutes}:{seconds:02d}:{milliseconds:03d}"
