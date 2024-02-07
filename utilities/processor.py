from pathlib import Path
from datetime import datetime, timedelta
from exif import Image
from logging import getLogger

from utilities.matcher import Matcher
from utilities.filter import Filter
from utilities.haversine import Haversine


_LOGGER = getLogger(__name__.split('.')[-1])


class Processor:
    """High-level class designed to oversee speed calculations for multiple images"""

    def __init__(self,
                 image: Path,
                 compare_images: list[Path],
                 gsd: int,
                 angle_tolerance: float,
                 distance_tolerance: float,
                 show_matches: bool = False) -> None:
        self._IMAGE = image
        self._COMPARE_IMAGES = compare_images
        self._GSD = gsd
        self._ANGLE_TOLERANCE = angle_tolerance
        self._DISTANCE_TOLERANCE = distance_tolerance
        self._SHOW_MATCHES = show_matches
        self._match_speeds = []
        self._position_speeds = []


    def _lazy_compute(self) -> bool:
        """Increase performance by making sure computation only happens once"""
        if len(self._position_speeds) > 0:
            return False

        self._compute_speeds()
        return True


    def _compute_speeds(self) -> None:
        """Find speeds for each image through GeoTags and OpenCV"""
        for image in self._COMPARE_IMAGES:
            self._position_speeds += [self._speed_from_position(image)]

            try:
                match_speed = self._speed_from_matches(image)
            except Exception as exc:
                _LOGGER.error(f"Could not match images: {exc}")
            else:
                if match_speed is None:
                    _LOGGER.warn(f"Not enough matches for ({self._IMAGE.name}) -> ({image.name}) to calculate speed")
                else:
                    self._match_speeds += [match_speed]


    @staticmethod
    def _timestamp(image: Path) -> datetime:
        """Get image timestamps from metadata"""
        with open(image, "rb") as image_file:
            img = Image(image_file)
            timestamp_str = img.get("datetime_original")

        return datetime.strptime(timestamp_str, "%Y:%m:%d %H:%M:%S")


    @staticmethod
    def _time_delta(image1: Path, image2: Path) -> timedelta:
        """Find the difference in capture times between two images"""
        timestamp1 = Processor._timestamp(image1)
        timestamp2 = Processor._timestamp(image2)

        return timestamp1 - timestamp2


    def _speed_from_matches(self, compare_image: Path) -> float:
        """Calculate the speed between two images using OpenCV matching"""
        matcher = Matcher(self._IMAGE, compare_image)
        coordinates = matcher.get_matches()

        if self._SHOW_MATCHES:
            matcher.show_matches()

        coordinate_filter = Filter(coordinates, self._ANGLE_TOLERANCE, self._DISTANCE_TOLERANCE)
        filtered = coordinate_filter.filtered

        if filtered == []:
            return None

        if self._SHOW_MATCHES:
            Matcher.show_coordinates(self._IMAGE, compare_image, filtered)

        feature_distance = coordinate_filter.distance
        time = Processor._time_delta(self._IMAGE, compare_image).total_seconds()

        # GSD is given in centimeters per pixel.
        # We want it in meters and there are 100cm per meter.
        real_distance = feature_distance * (self._GSD / 100)
        speed = real_distance / time

        return speed


    def _speed_from_position(self, compare_image: Path) -> float:
        """Calculate the speed between two images using GeoTags and the Haversine formula"""
        time = Processor._time_delta(self._IMAGE, compare_image).total_seconds()
        haversine = Haversine(self._IMAGE, compare_image)

        real_distance = haversine.get_distance()
        speed = real_distance / time

        return speed
    
    
    def compute_speeds(self) -> bool:
        """Call to explicitly compute speeds"""
        return self._lazy_compute()


    def log_speeds(self) -> None:
        """Log beautified speeds through the root logger"""
        self._lazy_compute()
        _LOGGER.info(f"Image Speeds ({', '.join([str(round(speed, 5)) for speed in self._match_speeds])})")
        _LOGGER.info(f"GeoTag Speeds ({', '.join([str(round(speed, 5)) for speed in self._position_speeds])})")


    @property
    def match_speeds(self) -> list[float]:
        """List of speeds based on OpenCV matches between the images"""
        self._lazy_compute()
        return self._match_speeds


    @property
    def position_speeds(self) -> list[float]:
        """List of speeds basead on from image GeoTags and the Haversine formula"""
        self._lazy_compute()
        return self._position_speeds
