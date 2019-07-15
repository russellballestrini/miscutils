from ago import human

from datetime import datetime

def generate_password(size=32):
    """Return a system generated password"""
    from string import letters, digits
    from random import choice

    pool = letters + digits
    return "".join([choice(pool) for i in range(size)]).encode("utf-8")


def timestamp_to_datetime(timestamp):
    """Accepts a timestamp and returns a date string"""
    return datetime.fromtimestamp(timestamp / 1000.0)


def timestamp_to_date_string(timestamp):
    return timestamp_to_datetime(timestamp).strftime("%b %d, %Y %I:%M %P")


def timestamp_to_ago_string(timestamp):
    """Accepts a timestamp and returns a human readable string"""
    return human(timestamp_to_datetime(timestamp), 2, abbreviate=True)
