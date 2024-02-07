from pathlib import Path
from random import choice
from re import match
from shutil import copy
from logging import getLogger
from os import remove


_LOGGER = getLogger(__name__.split('.')[-1])


class ImageUtils:

    @staticmethod
    def purge_images(image_folder: Path) -> None:
        """Clear a directory of recently taken images"""
        for file in image_folder.iterdir():
            if not file.is_file():
                continue

            if not file.name.startswith("img-"):
                continue

            remove(file)
            _LOGGER.warning(f"Purged \"{file.name}\"")


    @staticmethod
    def prune_images(image_folder: Path, max_images: int) -> list[Path]:
        """Remove excess images from a folder to stay under the limit"""
        images = sorted([f for f in image_folder.iterdir() if f.is_file() and f.name.startswith("img-")])

        while len(images) > max_images:
            remove(images.pop(0))
            _LOGGER.info(f"Removed \"{images[0].name}\"")

        return images


class Camera:
    """Replicate a PiCamera for debugging using previous photos"""

    def __init__(self, folder_path: str = ".photos", min_group_size: int = 6, group_override: int = None) -> None:
        self._folder_path = Path(folder_path)
        self._files = sorted([f for f in self._folder_path.iterdir() if f.is_file() and f.name.startswith("photo")])
        self._groups = self._group_files(min_group_size)

        if group_override:
            self._current_group = self._groups[group_override]
        else:
            self._current_group = choice(self._groups)


    @staticmethod
    def _get_file_index(file: Path) -> int:
        """Fetches the number associated with an image name"""
        numbers = match(r"(\d+)", file.stem.split("_")[-1])

        if numbers is None:
            return None

        return int(numbers.group(0))


    def _group_files(self, min_group_size: int) -> list[list[Path]]:
        """Group images with adjacent numbers into lists"""
        groups = []
        files = self._files.copy()

        while len(files) > 0:
            group = [files.pop(0)]

            while files and (Camera._get_file_index(files[0]) - Camera._get_file_index(group[-1]) == 1):
                group += [files.pop(0)]

            groups += [group]

        return [sub_group for sub_group in groups if len(sub_group) >= min_group_size]


    def capture(self, path: str) -> None:
        """Emulates the PiCamera capture"""
        if not self._current_group:
            raise FileNotFoundError()

        image = str(self._current_group.pop(0))
        copy(image, path)
