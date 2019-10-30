"""
Original Sourcecode pulled from:

https://thadeusb.com/weblog/2010/10/10/python_scale_hex_color/
"""

def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val


def hex_color_scale(hex_str, scale_factor):
    """
    Scales a hex string by ``scale_factor``. Returns scaled hex string.

    To darken the color, use a float value between 0 and 1.
    To brighten the color, use a float value greater than 1.

    >>> hex_color_scale("#DF3C3C", .5)
    #6F1E1E
    >>> hex_color_scale("#52D24F", 1.6)
    #83FF7E
    >>> hex_color_scale("#4F75D2", 1)
    #4F75D2
    """

    hex_str = hex_str.strip('#')

    if scalefactor < 0 or len(hex_str) != 6:
        return hex_str

    r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16)

    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)

    return "#%02x%02x%02x" % (r, g, b)
