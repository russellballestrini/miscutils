from ago import human

from datetime import datetime


def generate_password(size=32):
    """Return a system generated password"""
    from string import letters, digits
    from random import choice

    pool = letters + digits
    return "".join([choice(pool) for i in range(size)]).encode("utf-8")


def get_int_or_bool_or_none_or_str(value):
    """
    Given a string value pulled from a configuration file,
    this function attempts to return the value with the proper type.
    """
    try:
        return int(value)
    except ValueError:
        if value.lower() in {"yes", "y", "true", "y"}:
            return True
        elif value.lower() in {"no", "n", "false", "f"}:
            return False
        elif value.lower() == "none":
            return None
        return str(value)


def get_children_settings(settings, parent_key):
    """
    Accept a settings dict and parent key, return dict of children

    For example:

      auth_tkt.hashalg = md5

    Results to:

      {'auth_tkt.hashalg': 'md5'}

    This function returns the following:

      >>> get_children_settings({'auth_tkt.hashalg': 'md5'}, 'auth_tkt')
      {'hashalg': 'md5'}

    """
    # needed to support expanding ENV vars from ini.
    from os.path import expandvars

    # the +1 is the . between parent and child settings.
    parent_len = len(parent_key) + 1
    children = {}
    for key, value in settings.items():
        if parent_key in key:
            # expandvars replaces template with ENV vars.
            children[key[parent_len:]] = get_int_or_bool_or_none_or_str(
                expandvars(value)
            )
    return children


def timestamp_to_datetime(timestamp):
    """Accepts a milliseconds timestamp integer and returns a datetime"""
    return datetime.fromtimestamp(timestamp / 1000.0)


def timestamp_to_date_string(timestamp):
    return timestamp_to_datetime(timestamp).strftime("%b %d, %Y %I:%M %P")


def datetime_to_timestamp(dt):
    """returns an integer timestamp in milliseconds"""
    epoch_dt = datetime(1970, 1, 1)
    return (dt - epoch_dt).total_seconds() * 1000


def timestamp_to_ago_string(timestamp):
    """Accepts a timestamp and returns a human readable string"""
    return human(timestamp_to_datetime(timestamp), 2, abbreviate=True)


def dollars_to_cents(dollars):
    return int(float(dollars) * 100)


def cents_to_dollars(cents):
    return int(cents) / 100.0
