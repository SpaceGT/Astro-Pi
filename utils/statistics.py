"""Helps calculate statistics."""

import logging

import numpy

_LOGGER = logging.getLogger(__name__)


def mean(data: list[float]) -> float:
    """Calculate the mean for a list of data."""
    return float(numpy.mean(data))


def median(data: list[float]) -> float:
    """Calculate the median for a list of data."""
    return float(numpy.median(data))


def std(data: list[float]) -> float:
    """Calculate the standard deviation for a list of data."""
    return float(numpy.std(data))


def iqr(data: list[float]) -> float:
    """Calculate the interquartile range for a list of data."""
    q1: float
    q3: float
    q1, q3 = numpy.percentile(data, [75, 25])
    return q3 - q1


def filter(data: list[float], threshold: float) -> list[float]:
    """Remove outliers from a list of data."""
    mean_ = mean(data)
    std_ = std(data)

    if std_ == 0:
        return data

    lower = mean_ - threshold * std_
    upper = mean_ + threshold * std_

    result: list[float] = []
    for value in data:
        if lower < value < upper:
            result.append(value)

    return result


def weigh(values: list[tuple[float, float]]) -> float:
    """Average a list of values with a skew towards higher weights."""
    total = sum(value[0] * value[1] for value in values)
    weight = sum(value[1] for value in values)
    return total / weight
