from math import atan2, degrees, sqrt
from numpy import median, subtract, percentile, mean, std

class Filter:
    """Filter sets of coordinates by removing outliers and anomalies"""

    def __init__(self, coordinates: list[tuple[tuple, tuple]],
                 angle_tolerance: float,
                 distance_tolerance: float,
                 filter_cutoff: int = 100) -> None:
        self._COORDINATES = coordinates
        self._ANGLE_TOLERANCE = angle_tolerance
        self._DISTANCE_TOLERANCE = distance_tolerance
        self._FILTER_CUTOFF = filter_cutoff
        self._filtered = None


    def _lazy_compute(self) -> bool:
        """Increase performance by making sure computation only happens once"""
        if self._filtered is not None:
            return False

        self._compute_filter()
        return True


    @staticmethod
    def _calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate the distance between two points using the Pythagorean theorem"""
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    @staticmethod
    def _calculate_direction(x1: float, y1: float, x2: float, y2: float) -> float:
        """Find the angle relative to the x-axis from a line with two points"""
        return degrees(atan2(y2 - y1, x2 - x1))


    @staticmethod
    def _is_outlier(value, median: float, tolerance: float, absolute: bool = True) -> bool:
        """Check if a value is within a given tolerance around the median"""
        limit = tolerance if absolute else median * tolerance

        if value > median + limit:
            return True

        if value < median - limit:
            return True

        return False


    def _median_direction(self) -> tuple[float, float]:
        """Find the spread and median angle of all pairs of co-ordinates"""
        angles = []
        for (x1, y1), (x2, y2) in self._COORDINATES:
            angles += [Filter._calculate_direction(x1, y1, x2, y2)]

        direction = median(angles)
        iqr = subtract(*percentile(angles, [75, 25]))

        return direction, iqr


    def _median_distance(self) -> tuple[float, float]:
        """Find the spread and median distance between all pairs of co-ordinates"""
        distances = []
        for (x1, y1), (x2, y2) in self._COORDINATES:
            distances += [Filter._calculate_distance(x1, y1, x2, y2)]

        distance = median(distances)
        iqr = subtract(*percentile(distances, [75, 25]))

        return distance, iqr


    def _mean_distance(self) -> float:
        """Find the mean and standard deviation of all filtered co-ordinates"""
        distances = []
        for (x1, y1), (x2, y2) in self._filtered:
            distances += [Filter._calculate_distance(x1, y1, x2, y2)]

        distance = mean(distances)
        sd = std(distances)

        return distance, sd


    def _compute_filter(self) -> None:
        """Create a list of data with outliers and anomalies removed"""
        direction_median, _ = self._median_direction()
        distance_median, _ = self._median_distance()

        self._filtered = []
        for (x1, y1), (x2, y2) in self._COORDINATES:
            direction = Filter._calculate_direction(x1, y1, x2, y2)
            distance = Filter._calculate_distance(x1, y1, x2, y2)

            if Filter._is_outlier(direction, direction_median, self._ANGLE_TOLERANCE, True):
                continue

            if Filter._is_outlier(distance, distance_median, self._DISTANCE_TOLERANCE, False):
                continue

            self._filtered += [((x1, y1), (x2, y2))]

        if len(self._filtered) < self._FILTER_CUTOFF:
            self._filtered = []


    @property
    def filtered(self) -> list[tuple[tuple, tuple]]:
        """Pairs of co-ordinates with with outliers and anomalies removed"""
        self._lazy_compute()
        return self._filtered


    @property
    def distance(self) -> float:
        """Mean distance based on filtered data"""
        self._lazy_compute()
        distance, _ = self._mean_distance()
        return distance
