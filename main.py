from config import Config
from utilities.processor import Processor
from utilities.data import Data
from utilities.camera import ImageUtils

from logging import getLogger
from datetime import datetime, timedelta
from time import sleep


_CONFIG = Config()
_LOGGER = getLogger(__name__)


try:
    from picamera import PiCamera as Camera
    _LOGGER.warning("Using real PiCamera")
except ImportError:
    from utilities.camera import Camera
    _LOGGER.warning("Using simulated PiCamera")


def main() -> None:
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=_CONFIG.RUN_DURATION)

    _CONFIG._IMAGE_PATH.mkdir(exist_ok=True)
    ImageUtils.purge_images(_CONFIG.IMAGE_PATH)

    camera = Camera()

    all_image_speeds = []
    all_geotag_speeds = []

    image_count = 0

    _LOGGER.info("Astro-Pi Started\n")

    while datetime.now() < end_time:
        next_image_time = datetime.now() + timedelta(seconds=_CONFIG.IMAGE_INTERVAL)

        image_name = f"img-{image_count}.jpg"
        camera.capture(str(_CONFIG.IMAGE_PATH / image_name))
        image_count += 1

        if image_count == 1:
            _LOGGER.info(f"Taken initial image \"images\\{image_name}\"")
            sleep(max((next_image_time - datetime.now()).total_seconds(), 0))
            continue

        _LOGGER.info(f"Taken image \"images\\{image_name}\"")

        images = ImageUtils.prune_images(_CONFIG.IMAGE_PATH, _CONFIG.IMAGE_LOOKBEHIND)
        base_image = images.pop()

        _LOGGER.info(f"Comparing ({base_image.name}) -> ({', '.join([image.name for image in images])})")

        processor = Processor(
            base_image,
            images,
            12648,
            _CONFIG.MATCH_ANGLE_TOLERANCE,
            _CONFIG.MATCH_DISTANCE_TOLERANCE,
            _CONFIG.VIEW_MATCHES
        )

        processor.compute_speeds()
        processor.log_speeds()

        all_geotag_speeds += processor.position_speeds
        geotag_data = Data(all_geotag_speeds, _CONFIG.ANOMALOUS_DEVIATION)
        geotag_data.log_statistics("Total GeoTag Speed:")

        all_image_speeds += processor.match_speeds
        if len(all_image_speeds) >= 5: # Image matching can be unreliable so we avoid it if there is not enough data
            image_data = Data(all_image_speeds, _CONFIG.ANOMALOUS_DEVIATION)
            image_data.log_statistics("Total Image Speed:")

            average_speed = Data.weighted_mean(geotag_data.mean, geotag_data.weight, image_data.mean, image_data.weight) / 1000

        else:
            _LOGGER.warning("Total Image Speed: NO_DATA")
            average_speed = geotag_data.mean / 1000

        with open(_CONFIG.BASE_DIR / "result.txt", "w") as output:
            output.write(f"{average_speed:#.5g} km/s")

        _LOGGER.info(f"Final Speed: {average_speed:#.5g} km/s - Saved to \"results.txt\"\n")
        
        sleep(max((next_image_time - datetime.now()).total_seconds(), 0))


if __name__ == "__main__":
    main()
