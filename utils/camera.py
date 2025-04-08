"""Replicate a PiCamera for debugging using previous photos."""

import logging
import os
import random
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from exif import Image

_LOGGER = logging.getLogger(__name__)


def _get_camera() -> Any:
    try:
        from picamera import PiCamera

    except ImportError:
        _LOGGER.info("Using simulated PiCamera")
        return FakeCamera()

    else:
        _LOGGER.info("Using real PiCamera")
        return PiCamera()


def _get_images(image_folder: Path) -> list[Path]:
    return sorted(
        (
            f
            for f in image_folder.iterdir()
            if f.is_file() and f.name.startswith("img-")
        ),
        key=lambda img: int(img.stem[4:]),
    )


def purge_images(image_folder: Path) -> None:
    """Clear a directory of recently taken images."""
    for file in image_folder.iterdir():
        if not file.is_file():
            continue

        if not file.name.startswith("img-"):
            continue

        os.remove(file)
        _LOGGER.warning(f'Purged "{file.name}"')


def count_images(image_folder: Path) -> int:
    return len(_get_images(image_folder))


def prune_images(image_folder: Path, max_images: int) -> list[Path]:
    """Remove excess images from a folder to stay under the limit."""
    images = _get_images(image_folder)

    while len(images) > max_images:
        _LOGGER.info(f'Removing "{images[0].name}"')
        os.remove(images.pop(0))

    return images


def timestamp(image: Path) -> datetime:
    """Get image timestamps from metadata"""
    with open(image, "rb") as image_file:
        img = Image(image_file)
        capture_time: str = img.get("datetime_original")

    return datetime.strptime(capture_time, "%Y:%m:%d %H:%M:%S")


def dimensions(image: Path) -> tuple[int, int]:
    """Get image dimensions from metadata"""
    with open(image, "rb") as image_file:
        img = Image(image_file)
        width: int = img.get("image_width")
        height: int = img.get("image_height")

    return width, height


def _photo_index(file: Path) -> int:
    """Fetches the number associated with a photo name."""
    numbers = re.match(r"(\d+)", file.stem.split("_")[-1])
    assert numbers is not None
    return int(numbers.group(0))


class Camera:
    """Wrapper used for taking photos."""

    def __init__(self) -> None:
        self.image_count = 0
        self.camera = _get_camera()

    def capture(self, path: Path, name: Union[str, None] = None) -> Path:
        self.image_count += 1

        if name:
            image_path = path / name
        else:
            image_path = path / f"img-{self.image_count}.jpg"

        self.camera.capture(str(image_path))
        return image_path


class FakeCamera:
    """Replicate a PiCamera for debugging using previous photos."""

    def __init__(
        self,
        folder_path: str = ".photos",
        min_group_size: int = 6,
        group_override: Union[int, None] = None,
    ) -> None:
        self._folder_path: Path = Path(folder_path)
        self._files: list[Path] = sorted(
            [
                f
                for f in self._folder_path.iterdir()
                if f.is_file() and f.name.startswith("photo")
            ]
        )
        self._groups: list[list[Path]] = self._group_files(min_group_size)

        self._current_group: list[Path] = []
        if group_override:
            self._current_group = self._groups[group_override]
        else:
            self._current_group = random.choice(self._groups)

    def _group_files(self, min_group_size: int) -> list[list[Path]]:
        """Group images with adjacent numbers into lists."""
        groups: list[list[Path]] = [[]]

        for current, next in zip(self._files, self._files[1:]):
            groups[-1].append(current)

            current_index = _photo_index(current)
            next_index = _photo_index(next)

            if next_index != current_index + 1:
                groups.append([])

        groups[-1].append(self._files[-1])

        result: list[list[Path]] = []
        for group in groups:
            if len(group) >= min_group_size:
                result.append(group)

        return result

    def capture(self, path: str) -> None:
        """Emulates the PiCamera capture."""
        if not self._current_group:
            raise FileNotFoundError()

        image = str(self._current_group.pop(0))
        shutil.copy(image, path)
