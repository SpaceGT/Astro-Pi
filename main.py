"""Entry point for Astro-Pi"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Union

import config
from utils import camera, speeds, statistics
from utils.camera import Camera

_LOGGER = logging.getLogger(__name__)


def sleep_until(date: datetime) -> None:
    time.sleep(max((date - datetime.now()).total_seconds(), 0))


def update_images(camera_: Camera) -> Union[list[Path], None]:
    image_count = camera.count_images(config.IMAGE_PATH)
    image = camera_.capture(config.IMAGE_PATH)

    if not image_count:
        _LOGGER.info(f'Taken initial image "images/{image.name}"')
        return None

    _LOGGER.info(f'Taken image "images/{image.name}"')
    return camera.prune_images(config.IMAGE_PATH, config.IMAGE_LOOKBEHIND + 1)


def update_speeds(
    base_image: Path,
    compare_images: list[Path],
    match_speeds: list[float],
    geotag_speeds: list[float],
) -> None:
    _LOGGER.info(
        f"Comparing ({base_image.name}) -> ({', '.join([image.name for image in compare_images])})"
    )

    last_match_speeds, last_geotag_speeds = speeds.compute_speeds(
        base_image, compare_images
    )
    match_speeds.extend(last_match_speeds)
    geotag_speeds.extend(last_geotag_speeds)

    geotags_result = speeds.process_geotags(geotag_speeds)
    matches_result = speeds.process_matches(match_speeds)

    if not any((geotags_result, matches_result)):
        _LOGGER.info("Insufficient data for final speed")
        return

    average_speed = statistics.weigh(
        list(filter(None, (geotags_result, matches_result)))
    )
    with open(config.BASE_DIR / "result.txt", "w") as output:
        output.write(f"{average_speed:#.5g} km/s\n")

    _LOGGER.info(f'Final Speed: {average_speed:#.5g} km/s - Saved to "results.txt"')


def main() -> None:
    config.setup_logging()

    start_time = datetime.now()
    end_time = start_time + config.RUN_DURATION

    config.IMAGE_PATH.mkdir(exist_ok=True)
    camera.purge_images(config.IMAGE_PATH)
    camera_ = Camera()

    match_speeds: list[float] = []
    geotag_speeds: list[float] = []

    _LOGGER.info("Astro-Pi Started")

    while datetime.now() < end_time:
        next_image_time = datetime.now() + config.IMAGE_INTERVAL
        images = update_images(camera_)

        if images is not None:
            update_speeds(images.pop(), images[::-1], match_speeds, geotag_speeds)

        sleep_until(next_image_time)


if __name__ == "__main__":
    main()
