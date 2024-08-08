# iot-net-planner
A set of tools written in Python for planning an [IoT network](https://blogs.cornell.edu/iotnetwork/what-is-a-public-iot-network/). The primary features for this package are:
- [DSM creation](#dsm-creation)
- [Packet reception rate](https://blogs.cornell.edu/iotnetwork/how-do-you-set-a-network-up/communication-between-gateways-and-devices/) prediction
- [Gateway](https://blogs.cornell.edu/iotnetwork/how-do-you-set-a-network-up/gateway-set-up/) placement optimization

## Installation

### Python Users
For users with knowledge about Python, to install the package:
- Clone the repository
- Navigate to the directory containing src
- (Optional) Create and activate a new Python [virtual environment](https://docs.python.org/3/library/venv.html)
- Run `pip install -e .` to install the package in edit mode. **You may need to add the "src" directory to PYTHONPATH**.

### Non-Python Users
For users without knowledge of Python, to install the package:
1. [Install Python](https://realpython.com/installing-python/)
1. Download the repository here by clicking the green "<> Code" button and clicking "Download ZIP"
1. Extract the zip
1. Navigate to the unzipped directory in a command prompt
1. Create a [Python environment](https://docs.python.org/3/library/venv.html) with the command `python3 -m venv iotvenv`
1. Activate the environment with `source iotvenv/bin/activate`
1. Install the package with `pip install .`
1. Note that if you close the command prompt, you need to perform steps 4. and 6. again when opening a new prompt

## Usage
Documentation is in its early stages. The documented pipeline stages are:
- [DSM Creation](#dsm-creation)
- [Defining a Coverage Area](#creating-coverage-area)

### DSM Creation
A Digital Surface Model ([DSM](https://en.wikipedia.org/wiki/Digital_elevation_model)) is an image that gives an elevation at every point in an area. Our models use this elevation to predict how much coverage a gateway might provide. As an example, here is an aspect render for a DSM created for an area around Ithaca, New York:

![Image showing an aspect render](https://i.imgur.com/Q1ALz0z.jpeg)

The rest of this DSM Creation section will cover how you could create a DSM for that area. The method will work for most of the United States. For municipalities in the United States, the [United States Geological Survery](https://www.usgs.gov/) (USGS) provides free Lidar data for creating a DSM. 

To create a DSM using USGS data, head to the [USGS Lidar Explorer](https://apps.nationalmap.gov/lidar-explorer/#/). In the menu on the right, click the box next to "Show where Lidar is available" to see if coverage is available in your area.

![Image showing the location of the lidar availability toggle on the USGS website](https://i.imgur.com/gGI4fGe.png)

It is alright if there are some gaps, but consider finding another source of geodata if much of the area is not available. Uncheck the "Show where Lidar is available" box once you have seen if your area is available. Now you can define the area the DSM will cover. You will choose a rectangular region; it should completely enclose the desired coverage area and all potential gateway locations. Check the box "Define Area of Interest" (1), click the rectangle icon in the top left of the map (2), click to define he first corner of the desired region (3), and then click to define the second corner of the region (4). 

![Image showing the locations of (1) - (4) on the USGS website](https://i.imgur.com/T7ShtJe.png)

Next, click on the "LIDAR PROCESSING" button on the right.

![Image showing locations of LIDAR PROCESSING on the USGS website](https://i.imgur.com/wFoFQcg.png)

In the next menu, ensure that your region is still selected by zooming in on the map. Next, click the circle next to "TIFF" to select it as the output (1), set "OutputType" to "idw" by clicking on the dropdown and selecting the corresponding value (2), and then click "PROCESS IN CLOUD" to start downloading (3).

![Image showing locations of (1) - (3) on the USGS website](https://i.imgur.com/7jMHDVn.png)

After the green bar fills at the top of the screen, the server will start creating the requested DSM. Click "SHOW REQUESTS" (1) and press the refresh icon (2) to check on the status of the request. **Note:** the progress will only update when the refresh icon is clicked, the website will not tell you the request has been completed until you refresh. Make sure to refresh every once and a while to check if the request has been completed.

![Image showing locations of (1) and (2) on the USGS website](https://i.imgur.com/ZQTsqgw.png)

The process may take a long time, especially for high resolutions or large areas. The status menu will say "Status: Processing Completed!" when the request is done processing. Click the "Download tif #0" link to download the completed DSM. You can rename and move the file, make sure that it still has the ".tif" file extension and remember where it is kept on the computer.

![Image showing a completed request menu on the USGS website](https://i.imgur.com/wn6CUNL.png)

The resulting DSM may still have small holes to fill. For example, here is a DSM of Ithaca before filling (it corresponds to the aspect render from the start of the section):

![Image showing a DSM with holes](https://i.imgur.com/8JKHxpZ.png)

In the command prompt, run `python examples/fill_script.py dsm_path new_path` where `dsm_path` is the path to the DSM file on your computer and `new_path` is the path where the filled DSM will be placed. After filling, the DSM now looks like this:

![Image showing a filled DSM](https://i.imgur.com/7oD3JX2.png)

### Creating Coverage Area
You can define a desired coverage area using [Google My Maps](https://www.google.com/maps/about/mymaps/), you will need to create a Google account if you do not already have one. After signing in, click "CREATE A NEW MAP" to begin.

![Image showing the CREATE A NEW MAP button on Google Maps](https://i.imgur.com/QJs981e.png)

Give the map a name by clicking on "Untitled map," entering a name and (optionally) a description, and clicking "Save." Also rename the "Untitled layer" below.

![Image showing the Untitled Map button on Google Maps](https://i.imgur.com/Pp5o2vA.png)

Zoom in to your desired coverage area. Click the "Draw a line" tool under the search bar (1) and click "Add line or shape" (2).

![Image showing locations (1) and (2) on Google Maps](https://i.imgur.com/4E9VUKq.png)

Now click the map to start drawing a polygon around the desired coverage area. Click the original point to complete the polygon.

![Image showing creating a polygon on Google Maps](https://i.imgur.com/cmLVmMr.png)

You can drag the polygon's vertices to move them, and click the midpoint between adjacent vertices to create a new vertex between them. To add more coverage polygons, first add a new layer with the "Add layer" button (1), then add a polygon as above. **Do not add multiple polygons to the same layer.** Make sure that the desired layer is selected when trying to add a polygon to it. The selected layer will have a colored bar on the left side of its box (2). To select a layer, you can click on the corresponding box.

![Image showing adding a new layer](https://i.imgur.com/H1iKkYl.png)

To export the map: click the three dots to the right of the map name (1), click "Export to KML/KMZ" (2), make sure that the "Entire Map" is selected if you have multiple layers, check "Export as KML instead of KMZ" (3), then click the blue "Download" button (4). You can rename and move the file, make sure that it still has the ".kml" file extension and remember where it is kept on the computer.

![Image showing export](https://i.imgur.com/JvRv5lr.png)

## Acknowledgement
The development of these tools was supported by the NSF under grant CNS-1952063.
