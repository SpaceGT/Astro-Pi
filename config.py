from pathlib import Path
from logging import getLogger, Formatter, StreamHandler, INFO, FileHandler
from sys import stdout


class Config:
    BASE_DIR = Path(__file__).parent

    def __init__(self) -> None:
        self._setup_logging()
        self._load_config()


    def _setup_logging(self) -> None:
        simple_formatter = Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        colored_formatter = Formatter("\u001b[30m%(asctime)s\u001b[0m \u001b[34m%(levelname)-8s\u001b[0m \u001b[32m%(name)-10s \u001b[0m %(message)s", "%Y-%m-%d %H:%M:%S")

        console_handler = StreamHandler(stdout)
        console_handler.setFormatter(colored_formatter)

        file_handler = FileHandler(Config.BASE_DIR / "info.log", mode="w", encoding="utf-8")
        file_handler.setFormatter(simple_formatter)

        root_logger = getLogger()
        root_logger.setLevel(INFO)

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)


    def _load_config(self) -> None:
        self._IMAGE_LOOKBEHIND = 3
        self._MATCH_ANGLE_TOLERANCE = 10
        self._MATCH_DISTANCE_TOLERANCE = 0.1
        self._ANOMALOUS_DEVIATION = 2
        self._IMAGE_INTERVAL = 10
        self._RUN_DURATION = 540
        self._VIEW_MATCHES = False
        self._IMAGE_PATH = Config.BASE_DIR / "images"


    @property
    def IMAGE_LOOKBEHIND(self) -> int:
        """Number of previous images to compare each new image to"""
        return self._IMAGE_LOOKBEHIND


    @property
    def MATCH_ANGLE_TOLERANCE(self) -> int:
        """All matches must have less then this angle deviation from the average"""
        return self._MATCH_ANGLE_TOLERANCE


    @property
    def MATCH_DISTANCE_TOLERANCE(self) -> int:
        """All matches must have their distance within this percentage of the average"""
        return self._MATCH_DISTANCE_TOLERANCE


    @property
    def ANOMALOUS_DEVIATION(self) -> int:
        """Values that are deviate more then this from the mean are classed as anomalies"""
        return self._ANOMALOUS_DEVIATION


    @property
    def VIEW_MATCHES(self) -> bool:
        """Opens up a match viewer after every OpenCV match for debugging"""
        return self._VIEW_MATCHES


    @property
    def IMAGE_INTERVAL(self) -> int:
        """Amount of seconds to wait after taking an image before another is taken"""
        return self._IMAGE_INTERVAL


    @property
    def RUN_DURATION(self) -> int:
        """Program will cleanly exit AFTER this time in seconds has elapsed"""
        return self._RUN_DURATION


    @property
    def IMAGE_PATH(self) -> Path:
        """Path where images from the camera are stored"""
        return self._IMAGE_PATH
