"""Performs high level speed calculations"""

import logging
from pathlib import Path
from typing import Union

import config

from . import geotags, matches, statistics

_LOGGER = logging.getLogger(__name__)


def compute_speeds(
    base_image: Path, compare_images: list[Path]
) -> tuple[list[float], list[float]]:
    """Find speeds for each image through GeoTags and OpenCV"""
    match_speeds: list[float] = []
    geotag_speeds: list[float] = []

    for compare_image in compare_images:
        match_speed, match_number = matches.compute_speed(
            base_image, compare_image, config.PERCENTAGE_ERROR
        )

        if not match_speed or match_number < config.MIN_IMAGE_MATCHES:
            _LOGGER.warning(
                f"Not enough matches for ({base_image.name}) -> ({compare_image.name}) to calculate speed"
            )
        else:
            match_speeds.append(match_speed)

        geotag_speeds.append(geotags.compute_speed(base_image, compare_image))

    pretty_match_speeds = ", ".join(f"{speed:.5f}" for speed in match_speeds)
    _LOGGER.info(f"Match Speeds ({pretty_match_speeds})")

    pretty_geotag_speeds = ", ".join(f"{speed:.5f}" for speed in geotag_speeds)
    _LOGGER.info(f"GeoTag Speeds ({pretty_geotag_speeds})")

    return match_speeds, geotag_speeds


def process_geotags(geotag_speeds: list[float]) -> Union[tuple[float, float], None]:
    if not geotag_speeds:
        _LOGGER.warning("Skipping GeoTag Speeds")
        return None

    filter_geotag_speeds = statistics.filter(geotag_speeds, config.ANOMALOUS_DEVIATION)

    if len(filter_geotag_speeds) < config.MIN_SPEEDS:
        _LOGGER.info("Insufficient data for total geotag speed")
        return None

    getotag_mean = statistics.mean(filter_geotag_speeds)
    getotag_std = statistics.std(filter_geotag_speeds)

    _LOGGER.info(
        f"Total GeoTag Speed: {getotag_mean:.5f} "
        + f"(SD: {getotag_std:.4g}) "
        + f"({len(geotag_speeds)- len(filter_geotag_speeds)} outliers rejected)"
    )

    return getotag_mean, getotag_std**-1


def process_matches(match_speeds: list[float]) -> Union[tuple[float, float], None]:
    if not match_speeds:
        _LOGGER.warning("Skipping Match Speeds")
        return None

    filter_match_speeds = statistics.filter(match_speeds, config.ANOMALOUS_DEVIATION)

    if len(filter_match_speeds) < config.MIN_SPEEDS:
        _LOGGER.info("Insufficient data for total match speed")
        return None

    match_mean = statistics.mean(filter_match_speeds)
    match_std = statistics.std(filter_match_speeds)

    _LOGGER.info(
        f"Total Match Speed: {match_mean:.5f} "
        + f"(SD: {match_std:.4g}) "
        + f"({len(match_speeds)- len(filter_match_speeds)} outliers rejected)"
    )

    return match_mean, match_std**-1
