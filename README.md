# Astro-Pi
A refactored version of my submission for the 2023-2024 [Mission Space Lab](https://astro-pi.org/mission-space-lab) competition.<br>
This project is designed to compute the real-time speed of the ISS to five significant figures.<br>

## Method
OpenCV is used to find matching features between sets of images which are converted into real-world distances.<br>
Image GeoTags and the Haversine formula are used to provide a second value for the the distance travelled.<br>

Multiple sets of speeds are then calculated using the differences in image capture times.<br>
A weighted average is done based on the variance of each set to calculate the final speed.<br>

This process is repeated over a configurable time period as new images are taken.<br>

## Reliability
Should OpenCV fail or find too little matches, the resulting speed will be discarded.<br>
Anomalous data is filtered out and the weighted average provides redundancy if one method proves inaccurate.<br>

## Testing
If you're using an Astro-Pi running [main.py](./main.py) will work without any further interaction.<br>
Options for debugging and general configuration are available in [config.py](./config.py).<br>

If the PiCamera module is not present a simulated camera will be used instead!<br>
Data will be drawn from `.photos/` which must be populated with [valid images](https://www.flickr.com/photos/raspberrypi/collections/72157722483243333/).<br>

This is designed to work with [Python 3.9](https://www.python.org/downloads/release/python-390/) (some dependencies do not work on the latest version).<br>
The [astro-pi-replay](https://pypi.org/project/astro-pi-replay/) package will pull all required modules!<br>

## Submission
To comply with Astro-Pi's [requirements](https://astro-pi.org/mission-space-lab/rulebook) the following changes were made before submission:<br>
- All python scripts were moved to the base directory.
- The location for storing images was changed to the base directory.
- Repository files not meeting file type restrictions were cut.
