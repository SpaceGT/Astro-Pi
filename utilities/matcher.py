from pathlib import Path
from cv2 import SIFT_create, imread, FlannBasedMatcher, drawMatchesKnn
from cv2 import resize, INTER_AREA, imshow, waitKey, destroyWindow
from cv2 import KeyPoint, drawMatches, DMatch

class Matcher:
    """Find pairs of matching co-ordinates between two images"""
    _TREES = 10
    _CHECKS = 100
    _K = 2

    def __init__(self, image: Path, compare_image: Path) -> None:
        self._WINDOW_NAME = f"{compare_image.name} -> {image.name} (Press 0 to exit)"
        self._IMAGE = imread(str(image), 0)
        self._COMPARE_IMAGE = imread(str(compare_image), 0)
        self._matches = None


    def _compute_features(self) -> None:
        """Find features in both images that can be used for matching"""
        sift = SIFT_create()
        self._image_keypoints, self._image_descriptors = sift.detectAndCompute(self._IMAGE, None)
        self._compare_image_keypoints, self._compare_image_descriptors = sift.detectAndCompute(self._COMPARE_IMAGE, None)


    def _compute_matches(self) -> None:
        """Find matches by finding similar features on both images"""
        index_params = dict(algorithm=5, trees=Matcher._TREES)
        search_params = dict(checks=Matcher._CHECKS)

        flann = FlannBasedMatcher(index_params, search_params)
        self._matches = flann.knnMatch(self._image_descriptors, self._compare_image_descriptors, k=Matcher._K)

        self._matches = [m for _, (m, _) in enumerate(self._matches)]
        self._matches = sorted(self._matches, key=lambda x: x.distance)


    def _lazy_compute(self) -> bool:
        """Increase performance by making sure computation only happens once"""
        if self._matches is not None:
            return False

        self._compute_features()
        self._compute_matches()

        return True


    def get_matches(self) -> list[tuple[tuple, tuple]]:
        """Get matching pairs of co-ordinates between the two images"""
        self._lazy_compute()

        coordinates = []
        for match in self._matches:
            x_base, y_base = self._image_keypoints[match.queryIdx].pt
            x_compare, y_compare = self._compare_image_keypoints[match.trainIdx].pt
            coordinates.append(((x_base, y_base), (x_compare, y_compare)))

        return coordinates


    def show_matches(self) -> None:
        """View computed matches in a window for debugging"""
        self._lazy_compute()

        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=(255, 0, 0),
                           flags=0)

        display_image = drawMatchesKnn(
            self._IMAGE, self._image_keypoints,
            self._COMPARE_IMAGE, self._compare_image_keypoints,
            [self._matches], None, **draw_params)

        resized_image = resize(display_image, (1600, 600), interpolation=INTER_AREA)
        imshow(self._WINDOW_NAME, resized_image)
        waitKey(0)
        destroyWindow(self._WINDOW_NAME)


    @staticmethod
    def show_coordinates(base_image: Path, compare_image: Path, coordinates: list[tuple], window_name: str = "") -> None:
        """View image co-ordinate matches in a window for debugging"""
        base_image_cv = imread(str(base_image), 0)
        compare_image_cv = imread(str(compare_image), 0)

        window_name = window_name or f"{base_image.name} -> {compare_image.name} (Press 0 to exit)"

        keypoints_base = []
        keypoints_compare = []

        for coord_base, coord_compare in coordinates:
            keypoints_base += [KeyPoint(coord_base[0], coord_base[1], 1)]
            keypoints_compare += [KeyPoint(coord_compare[0], coord_compare[1], 1)]

        # Make match objects for each index in the base array
        # Each match "links" co-ordinates with the same index
        # Distance is left to 0 as it is not needed to display the points
        matches = [DMatch(i, i, 0) for i in range(len(keypoints_base))]

        display_image = drawMatches(base_image_cv, keypoints_base, compare_image_cv, keypoints_compare, matches, None)
        resized_image = resize(display_image, (1600, 600), interpolation=INTER_AREA)
        imshow(window_name, resized_image)
        waitKey(0)
        destroyWindow(window_name)
