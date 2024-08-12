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
A Digital Surface Model ([DSM](https://en.wikipedia.org/wiki/Digital_elevation_model)) is an image that gives an elevation at every point in an area. Our models use this elevation to predict how much coverage a gateway might provide. We need a DSM that encloses the whole desired coverage region and all potential gateways. As an example, here is an aspect render for a DSM created for an area around Ithaca, New York:

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

In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of [non-python user instructions](#non-python-users)). Then, run `python examples/fill_script.py dsm_path new_path` where `dsm_path` is the path to the DSM file on your computer and `new_path` is the path where the filled DSM will be placed. **Note:** If any paths contain a space, that path should be wrapped in double quotes. After filling, the DSM now looks like this:

![Image showing a filled DSM](https://i.imgur.com/7oD3JX2.png)

### Creating Coverage Area
In this section you will define the area you want covered. This requires you have already [made a DSM](#dsm-creation) that fully covers the desired coverage region. You can define a desired coverage area using [Google My Maps](https://www.google.com/maps/about/mymaps/), you will need to create a Google account if you do not already have one. After signing in, click "CREATE A NEW MAP" to begin.

![Image showing the CREATE A NEW MAP button on Google Maps](https://i.imgur.com/QJs981e.png)

Give the map a name by clicking on "Untitled map," entering a name and (optionally) a description, and clicking "Save." Also rename the "Untitled layer" below.

![Image showing the Untitled Map button on Google Maps](https://i.imgur.com/Pp5o2vA.png)

Zoom in to your desired coverage area. Click the "Draw a line" tool under the search bar (1) and click "Add line or shape" (2).

![Image showing locations (1) and (2) on Google Maps](https://i.imgur.com/4E9VUKq.png)

Now click the map to start drawing a polygon around the desired coverage area. Click the original point to complete the polygon.

![Image showing creating a polygon on Google Maps](https://i.imgur.com/cmLVmMr.png)

You can drag the polygon's vertices to move them, and click the midpoint between adjacent vertices to create a new vertex between them. To add more coverage polygons, first add a new layer with the "Add layer" button (1), then add a polygon as above. **Do not add multiple polygons to the same layer.** Make sure that the desired layer is selected when trying to add a polygon to it. The selected layer will have a colored bar on the left side of its box (2). To select a layer, you can click on the corresponding box.

![Image showing adding a new layer](https://i.imgur.com/H1iKkYl.png)

To export the map: click the three dots to the right of the map name (1), click "Export to KML/KMZ" (2), make sure that the "Entire Map" is selected if you have multiple layers, check "Export as KML instead of KMZ" (3), then click the blue "Download" button (4). You can rename and move the file, make sure that it still has the ".kml" file extension and remember where it is kept on the computer. This is the area file.

![Image showing export](https://i.imgur.com/JvRv5lr.png)

Now you will create a demand point file. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python examples/demand_creation.py dsm_path area_path output_path points` where `dsm_path` is a path to the dsm file on your computer, `area_path` is a path to the area file on your computer, `output_path` is a path to the new file to be created ending in ".geojson", and `points` is a positive integer representing how many points will be generated. **Note:** If any paths contain a space, that path should be wrapped in double quotes. The higher the `points` number the more accurate coverage will be, but the longer computations will take. Larger areas will need more points. For reference, `1000` points is probably enough for the small area in the Ithaca example above. As another example, `8000` points was used for high-granularity coverage of lower Manhattan, Brooklyn, and the west side of Queens.

### Finding potential gateways
In this section you will define the potential locations that gateways can be placed. The package supports two methods for defining locations.
1. You can automatically generate potential locations [from building corners](#gateways-from-building-corners).
2. You can [manually place](#manual-gateway-placement) potential gateway locations for places that are likely to allow gateways.

If you have gateways that are already built the model can take the coverage it already provides into account. Make sure that prebuilt gateways are [manually](#manual-gateway-placement) input with corresponding "built" entries set to `1`. You can also combine potential gateways from the two methods into a [hybrid](#hybrid-gateway-placement). 

**Note:** all potential gateway locations should be in the DSM that you created. Additionally, if you draw a line segment from every potential gateway to every desired coverage point the whole segment should be in the DSM that was created. If you generated the DSM using the method above, the coverage area is completely within the DSM, and all potential gateway locations were within the DSM, you satisfy the segment criterion automatically.

#### Gateways from building corners
This section will show you how to generate a potential gateway file automatically from building corners. This requires a [DSM](#dsm-creation) and an [area file](#creating-coverage-area). In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python examples/fac_creation.py dsm_path area_path output_path` where `dsm_path` is a path to the dsm file on your computer, `area_path` is a path to the area file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes. After the command runs, there will be an ouput similar to `Generated x potential gateways` informing you how many potential gateways were found. More potential gateways will make the computations take longer. To generate fewer potential locations run the command `python examples/fac_creation.py dsm_path area_path output_path n_facs` where `n_facs` is how many locations you would like, and the rest of the parameters are the same as above. This will lead choose `n_facs` of the gateways that were found while trying to space them apart.

Generating using the Ithaca area file from above gives `40191` potential gateway locations. Asking for `250` of them gives the following gateways:

![Image showing the generated gateways for Ithaca](https://i.imgur.com/b2LnNPV.png)

#### Manual gateway placement
This section will show you how to manually define potential gateway locations. This requires a [DSM](#dsm-creation) unless you know the altitudes of all the potential gateway locations. For users with GeoPandas experience who want to make their own GeoDataFrame, go to [the first subsection](#users-with-geopandas-experience). For users without GeoPandas experience or want step-by-step instructions, go to [the second subsection](#users-without-geopandas-experience).
##### Users with GeoPandas experience
Create a GeoDataFrame with point geometry. There should be an entry for each potential gateway location. Optionally, add an "altitude" column that contains the height for each gateway location (for USGS DSMs the height above sea level in meters), or NaN for values to be filled by DSM. If no "altitude" column is present all values will be filled by DSM. Optionally, add a "built" column that contains `0` for gateways that have not been built or `1` for gateways that are already built. If no "built" column is present all gateways will be assumed to be unbuilt. **Make sure the GeoDataFrame has a coordinate reference system**. Write the GeoDataFrame to a geojson file.

If you had any NaNs in the altitude column you must fill them. There is a helper script for this if you already have a [DSM](#dsm-creation). In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python examples/manual_fac.py dsm_path gdf_path output_path` where `dsm_path` is a path to the dsm file on your computer, `gdf_path` is a path to the geojson file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes.

##### Users without GeoPandas experience
This section will show you how to manually define potential gateway locations. This requires a [DSM](#dsm-creation) unless you know the altitudes of all the potential gateway locations. This section assumes knowledge of a spreadsheet program. The example images will use [Google Sheets](https://workspace.google.com/products/sheets/), a free spreadsheet website, but any spreadsheet program that can export a ".csv" file will work.

Add columns called "latitude" and "longitude". If you know the altitude of some gateways then also add an "altitude" column. If some of the gateways are already built, add a "built" column.

![Image of an example sheet](https://i.imgur.com/EeB4C8I.png)

For each of the gateway locations follow these steps:
1. Input the latitude and longitude of the location. You can find a latitude and longitude by going to [Google Maps](https://www.google.com/maps/), right-clicking a location (1), and then clicking the top entry in the popout menu to copy the coordinates to clipboard (2). If you copy it to clipboard in this way you will need to separate the two numbers into the spreadsheet columns.

![Image of an example sheet](https://i.imgur.com/3nDy3u9.png)

2. Skip this step if you do not have an "altitude" column. If you know the altitude of the gateway, put its altitude (for USGS DSMs this is in meters above sea level) in the "altitude" column. If you do not know the gateway's altitude, put "NaN" (case sensitive).
   
3. Skip this step if you do not have a "built" column. If the gateway is already built, put a `1` in the "built" column. Otherwise, put a `0`.

After adding all the locations your spreadsheet will look something like the following (perhaps without the "altitude" and "built" columns):

![Image showing a small completed spreadsheet](https://i.imgur.com/A0TKV9z.png)

Download the spreadsheet as a ".csv" file. In Google Sheets you can do this by navigating File -> Download -> Comma Separated Values. You can rename and move the file, make sure that it still has the ".csv" file extension and remember where it is kept on the computer. This is the CSV file.

In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python examples/manual_fac.py dsm_path csv_path output_path` where `dsm_path` is a path to the dsm file on your computer, `csv_path` is a path to the csv file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes.

#### Hybrid gateway placement
This section is under construction. It will describe how to combine [building corner](#gateways-from-building-corners) and [manually placed](#manual-gateway-placement) gateways.

## Acknowledgement
The development of these tools was supported by the NSF under grant CNS-1952063.
