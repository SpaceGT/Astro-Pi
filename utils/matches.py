"""Generate and filter matches between images."""

import math
from pathlib import Path
from typing import Union

import cv2
from cv2 import DMatch, FlannBasedMatcher, KeyPoint

import config

from . import camera, statistics

COORDINATE = tuple[float, float]
MATCH_LIST = list[tuple[COORDINATE, COORDINATE]]

TREES = 10
CHECKS = 100
K_VALUE = 2


def get_GSD(width: int, height: int) -> float:
    """Scale a known GSD for different resolutions."""
    GSD = 12648  # Pixels / cm
    PIXELS = 4056 * 3040  # Resolution
    return GSD * PIXELS / (width * height) / 100


def compute_matches(image1: Path, image2: Path) -> MATCH_LIST:
    """Return a list of co-ordinate pairs of features between two images"""

    read_image1 = cv2.imread(str(image1), cv2.IMREAD_GRAYSCALE)
    read_image2 = cv2.imread(str(image2), cv2.IMREAD_GRAYSCALE)

    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(read_image1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(read_image2, None)

    index_params = dict(algorithm=5, trees=TREES)
    search_params = dict(checks=CHECKS)

    flann = FlannBasedMatcher(index_params, search_params)
    flann_matches = flann.knnMatch(descriptors1, descriptors2, k=K_VALUE)

    matches = sorted((match[0] for match in flann_matches), key=lambda x: x.distance)

    coordinates: MATCH_LIST = []
    for match in matches:
        x_base, y_base = keypoints1[match.queryIdx].pt
        x_compare, y_compare = keypoints2[match.trainIdx].pt
        coordinates.append(((x_base, y_base), (x_compare, y_compare)))

    return coordinates


def show_coordinates(image1: Path, image2: Path, coordinates: MATCH_LIST) -> None:
    """View image co-ordinate matches in a window for debugging"""
    read_image1 = cv2.imread(str(image1), cv2.IMREAD_GRAYSCALE)
    read_image2 = cv2.imread(str(image2), cv2.IMREAD_GRAYSCALE)

    window_name = f"{image1.name} -> {image2.name} (Press 0 to exit)"

    image1_keypoints = [KeyPoint(img1[0], img1[1], 1) for img1, _ in coordinates]
    image2_keypoints = [KeyPoint(img2[0], img2[1], 1) for _, img2 in coordinates]
    pairings = [DMatch(i, i, 0) for i in range(len(coordinates))]

    display_image = cv2.drawMatches(
        read_image1, image1_keypoints, read_image2, image2_keypoints, pairings, None
    )
    resized = cv2.resize(
        display_image, config.VIEW_RESOLUTION, interpolation=cv2.INTER_AREA
    )
    cv2.imshow(window_name, resized)
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)


def compute_speed(
    image1: Path, image2: Path, filter_percentage: int = 5
) -> tuple[Union[float, None], int]:
    """Calculate the average speed between the two input images"""
    matches = compute_matches(image1, image2)

    if not matches:
        return None, 0

    filtered = filter(matches, filter_percentage)

    if config.VIEW_MATCHES:
        show_coordinates(image1, image2, matches)
        show_coordinates(image1, image2, filtered)

    if not filtered:
        return None, 0

    distance, _ = _mean_distance(filtered)
    time = camera.timestamp(image1) - camera.timestamp(image2)

    width, height = camera.dimensions(image1)
    return distance * get_GSD(width, height) / abs(time.total_seconds()), len(filtered)


def filter(matches: MATCH_LIST, percentage_error: int = 5) -> MATCH_LIST:
    """Remove matches with abnormal lengths and directions."""
    error_factor = percentage_error / 100

    direction_median, _ = _median_direction(matches)
    distance_median, _ = _median_distance(matches)

    filtered: MATCH_LIST = []
    for (x1, y1), (x2, y2) in matches:
        direction = math.atan2(y2 - y1, x2 - x1)
        distance = math.hypot(x2 - x1, y2 - y1)

        if abs((direction - direction_median) / direction_median) > error_factor:
            continue

        if abs((distance - distance_median) / distance_median) > error_factor:
            continue

        filtered.append(((x1, y1), (x2, y2)))

    return filtered


def _median_direction(coordinates: MATCH_LIST) -> tuple[float, float]:
    """Find the spread and median angle of all pairs of co-ordinates"""
    angles: list[float] = []
    for (x1, y1), (x2, y2) in coordinates:
        angles.append(math.atan2(y2 - y1, x2 - x1))

    return statistics.median(angles), statistics.iqr(angles)


def _median_distance(coordinates: MATCH_LIST) -> tuple[float, float]:
    """Find the spread and median distance between all pairs of co-ordinates"""
    distances: list[float] = []
    for (x1, y1), (x2, y2) in coordinates:
        distances.append(math.hypot(y2 - y1, x2 - x1))

    return statistics.median(distances), statistics.iqr(distances)


def _mean_distance(coordinates: MATCH_LIST) -> tuple[float, float]:
    """Find the mean and standard deviation of all filtered co-ordinates"""
    distances: list[float] = []
    for (x1, y1), (x2, y2) in coordinates:
        distances.append(math.hypot(y2 - y1, x2 - x1))

    distance = statistics.mean(distances)
    std = statistics.std(distances)

    return distance, std
