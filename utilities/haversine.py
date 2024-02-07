from exif import Image
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

class Haversine:
    """Compute distance travelled using latitude and longitude"""
    _ISS_HEIGHT = 6779000

    def __init__(self, image: Path, compare_image: Path) -> None:
        self._IMAGE = image
        self._COMPARE_IMAGE = compare_image


    @staticmethod
    def _coordinates(image: Path) -> tuple[float, float]:
        """Get image latitude and longitude from metadata"""
        with open(image, "rb") as image_file:
            img = Image(image_file)
            lat_deg, lat_min, lat_sec = img.get("gps_latitude")
            lon_deg, lon_min, lon_sec = img.get("gps_longitude")

        latitude = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
        longitude = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600

        return latitude, longitude


    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float, r: float) -> float:
        """Wrapper for the haversine formula (https://en.wikipedia.org/wiki/Haversine_formula)"""
        rlat1 = radians(lat1)
        rlat2 = radians(lat2)

        rdlat = radians(lat2 - lat1)
        rdlon = radians(lon2 - lon1)

        a = (sin(rdlat / 2.0)**2
             + cos(rlat1) * cos(rlat2)
             * sin(rdlon / 2.0) ** 2)

        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return r * c


    def get_distance(self) -> float:
        """Calculate the distance travelled between the two input images"""
        lat1, lon1 = Haversine._coordinates(self._IMAGE)
        lat2, lon2 = Haversine._coordinates(self._COMPARE_IMAGE)

        distance = Haversine._haversine(lat1, lon1, lat2, lon2, Haversine._ISS_HEIGHT)
        return distance
