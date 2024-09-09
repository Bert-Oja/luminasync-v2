import colorsys

import webcolors


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB"""
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h / 360, s / 100, v / 100))


def rgb_to_hex(rgb):
    """Convert RGB to Hex"""
    return "#%02x%02x%02x" % rgb


def hex_to_rgb(hex_color):
    """Convert Hex to RGB"""
    hex_color = hex_color.lstrip("#")
    h_len = len(hex_color)
    return tuple(
        int(hex_color[i : i + h_len // 3], 16) for i in range(0, h_len, h_len // 3)
    )


def rgb_to_hsv(rgb):
    """Convert RGB to HSV and return as separate variables"""
    normalized_rgb = tuple([x / 255.0 for x in rgb])
    h, s, v = colorsys.rgb_to_hsv(*normalized_rgb)
    # Convert to 0-360 for hue and 0-100 for saturation and value
    return int(round(h * 360, 2)), int(round(s * 100, 2)), int(round(v * 100, 2))


def tuple_to_rgb_string(rgb_tuple):
    return ",".join(map(str, rgb_tuple))


def rgb_string_to_tuple(rgb_string):
    return tuple(map(int, rgb_string.split(",")))


def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(requested_color):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)
        actual_name = None
    return actual_name, closest_name
