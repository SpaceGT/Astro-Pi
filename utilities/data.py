from numpy import mean, std
from logging import getLogger


_LOGGER = getLogger(__name__.split('.')[-1])


class Data:
    """Aid in filtering data and calculating statistics"""

    def __init__(self, data: list, anomalous: int = 2) -> None:
        self._DATA = data
        self._ANOMALOUS = anomalous
        self._filtered = None


    @staticmethod
    def _is_outlier(value: float, mean: float, sd: float, threshold: float) -> bool:
        """Check if a value lies within a given threshold of the mean"""
        if value > mean + threshold * sd:
            return True

        if value < mean - threshold * sd:
            return True

        return False


    @staticmethod
    def weighted_mean(value1: float, weight1: float, value2: float, weight2: float) -> float:
        """Average two values with a preference for the one with the hightest weight"""
        return (value1 * weight1 + value2 * weight2) / (weight1 + weight2)


    def _lazy_compute(self) -> bool:
        """Increase performance by making sure computation only happens once"""
        if self._filtered is not None:
            return False

        self._compute_filter()
        return True


    def _compute_filter(self) -> None:
        """Create a list of data with outliers and anomalies removed"""
        mean_data = mean(self._DATA)
        sd = std(self._DATA)

        self._filtered = []
        for data in self._DATA:
            if Data._is_outlier(data, mean_data, sd, self._ANOMALOUS):
                continue

            self._filtered += [data]


    def log_statistics(self, leading_message: str = "") -> None:
        """Log beautified statistics through the root logger"""
        _LOGGER.info(f"{leading_message} {self.mean} (SD: {self.deviation}) ({self.rejected} outliers rejected)")


    @property
    def mean(self) -> float:
        """The mean value of the input data"""
        self._lazy_compute()
        return mean(self._filtered)


    @property
    def deviation(self) -> float:
        """The standard deviation of the input data"""
        self._lazy_compute()
        return std(self._filtered)


    @property
    def rejected(self) -> int:
        """The number of elements that were filtered from the original data"""
        self._lazy_compute()
        return len(self._DATA) - len(self._filtered)


    @property
    def weight(self) -> float:
        """A value inversely proportional to variance intended for use in weighted averages"""
        self._lazy_compute()
        return 1/std(self._filtered)**2 if std(self._filtered) > 0 else 1000
