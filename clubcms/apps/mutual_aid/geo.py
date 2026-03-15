"""Haversine distance calculation for mutual aid geo-search."""

import math


def haversine_km(lat1, lon1, lat2, lon2):
    """Return great-circle distance in km between two (lat, lon) points."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_coordinates(coord_string):
    """Parse a 'lat,lng' string into (float, float) or None."""
    if not coord_string or "," not in coord_string:
        return None
    parts = coord_string.split(",", 1)
    try:
        lat = float(parts[0].strip())
        lng = float(parts[1].strip())
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return (lat, lng)
    except (ValueError, IndexError):
        pass
    return None
