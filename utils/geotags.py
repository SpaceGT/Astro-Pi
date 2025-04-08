"""Compute distance travelled using latitude and longitude."""

from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

from exif import Image

from . import camera

ISS_HEIGHT = 6779000


def haversine(lat1: float, lon1: float, lat2: float, lon2: float, r: float) -> float:
    """Wrapper for the haversine formula (https://en.wikipedia.org/wiki/Haversine_formula)"""
    rlat1 = radians(lat1)
    rlat2 = radians(lat2)

    rdlat = radians(lat2 - lat1)
    rdlon = radians(lon2 - lon1)

    a = sin(rdlat / 2.0) ** 2 + cos(rlat1) * cos(rlat2) * sin(rdlon / 2.0) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return r * c


def coordinates(image: Path) -> tuple[float, float]:
    """Get image latitude and longitude from metadata"""
    with open(image, "rb") as image_file:
        img = Image(image_file)
        lat_deg, lat_min, lat_sec = img.get("gps_latitude")
        lon_deg, lon_min, lon_sec = img.get("gps_longitude")

    latitude = lat_deg + lat_min / 60 + lat_sec / 3600
    longitude = lon_deg + lon_min / 60 + lon_sec / 3600

    return latitude, longitude


def get_distance(image1: Path, image2: Path, height: float = ISS_HEIGHT) -> float:
    """Calculate the distance travelled between the two input images"""
    lat1, lon1 = coordinates(image1)
    lat2, lon2 = coordinates(image2)

    return haversine(lat1, lon1, lat2, lon2, height)


def compute_speed(image1: Path, image2: Path) -> float:
    """Calculate the average speed between the two input images"""
    time = camera.timestamp(image1) - camera.timestamp(image2)
    distance = haversine(*coordinates(image1), *coordinates(image2), ISS_HEIGHT)

    return distance / abs(time.total_seconds())
