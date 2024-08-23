# iot-net-planner
A set of tools written in Python for planning an [IoT network](https://blogs.cornell.edu/iotnetwork/what-is-a-public-iot-network/). The primary features for this package are:
- [DSM creation](#dsm-creation)
- [Packet reception rate](https://blogs.cornell.edu/iotnetwork/how-do-you-set-a-network-up/communication-between-gateways-and-devices/) prediction
- [Gateway](https://blogs.cornell.edu/iotnetwork/how-do-you-set-a-network-up/gateway-set-up/) placement optimization

## Contributors
- Sander Aarts
- Alfredo Rodriguez
- Ali Amadeh
- Jacob Dentes

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

## Documentation
For users with technical knowledge wanting fine grained control, the documentation can be found [here](https://jacob-dentes.github.io/iot_net_planner/).

## Usage
For users with a typical use case, this section will walk you through the stages of using the package:
- [DSM creation](#dsm-creation)
- [Defining a coverage area](#creating-coverage-area)
- [Defining potential gateways](#finding-potential-gateways)
- [Training a model](#training-a-model)
- [Making Predictions](#making-predictions)
- [Performing Optimization](#performing-optimization)
- [Viewing Results](#viewing-results)

### DSM Creation
A Digital Surface Model ([DSM](https://en.wikipedia.org/wiki/Digital_elevation_model)) is an image that gives an elevation at every point in an area. Our models use this elevation to predict how much coverage a gateway might provide. We need a DSM that encloses the whole desired coverage region and all potential gateways. As an example, here is an aspect render for a DSM created for an area around Ithaca, New York:

![Image showing an aspect render](https://i.imgur.com/Q1ALz0z.jpeg)

The rest of this DSM Creation section will cover how you could create a DSM for that area. The method will work for most of the United States. For municipalities in the United States, the [United States Geological Survery](https://www.usgs.gov/) (USGS) provides free Lidar data for creating a DSM. For municipalities outside the United States, you might look into the [USGS Earth Explorer](https://earthexplorer.usgs.gov/).

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

In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of [non-python user instructions](#non-python-users)). Then, run `python scripts/fill_script.py dsm_path new_path` where `dsm_path` is the path to the DSM file on your computer and `new_path` is the path where the filled DSM will be placed. **Note:** If any paths contain a space, that path should be wrapped in double quotes. After filling, the DSM now looks like this:

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

Now you will create a demand point file. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/demand_creation.py dsm_path area_path output_path points` where `dsm_path` is a path to the dsm file on your computer, `area_path` is a path to the area file on your computer, `output_path` is a path to the new file to be created ending in ".geojson", and `points` is a positive integer representing how many points will be generated. **Note:** If any paths contain a space, that path should be wrapped in double quotes. The higher the `points` number the more accurate coverage will be, but the longer computations will take. Larger areas will need more points. For reference, `1000` points is probably enough for the small area in the Ithaca example above. As another example, `8000` points was used for high-granularity coverage of lower Manhattan, Brooklyn, and the west side of Queens.

### Finding Potential Gateways
In this section you will define the potential locations that gateways can be placed. The package supports two methods for defining locations.
1. You can automatically generate potential locations [from building corners](#gateways-from-building-corners).
2. You can [manually place](#manual-gateway-placement) potential gateway locations for places that are likely to allow gateways.

If you have gateways that are already built the model can take the coverage it already provides into account. Make sure that prebuilt gateways are [manually](#manual-gateway-placement) input with corresponding "built" entries set to `1`. You can also combine potential gateways from the two methods into a [hybrid](#hybrid-gateway-placement). 

**Note:** all potential gateway locations should be in the DSM that you created. Additionally, if you draw a line segment from every potential gateway to every desired coverage point the whole segment should be in the DSM that was created. If you generated the DSM using the method above, the coverage area is completely within the DSM, and all potential gateway locations were within the DSM, you satisfy the segment criterion automatically.

#### Gateways from Building Corners
This section will show you how to generate a potential gateway file automatically from building corners. This requires a [DSM](#dsm-creation) and an [area file](#creating-coverage-area). In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/fac_creation.py dsm_path area_path output_path` where `dsm_path` is a path to the dsm file on your computer, `area_path` is a path to the area file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes. After the command runs, there will be an ouput similar to `Generated x potential gateways` informing you how many potential gateways were found. More potential gateways will make the computations take longer. To generate fewer potential locations run the command `python scripts/fac_creation.py dsm_path area_path output_path n_facs` where `n_facs` is how many locations you would like, and the rest of the parameters are the same as above. This will lead choose `n_facs` of the gateways that were found while trying to space them apart.

Generating using the Ithaca area file from above gives `40191` potential gateway locations. Asking for `250` of them gives the following gateways:

![Image showing the generated gateways for Ithaca](https://i.imgur.com/b2LnNPV.png)

#### Manual Gateway Placement
This section will show you how to manually define potential gateway locations. This requires a [DSM](#dsm-creation) unless you know the altitudes of all the potential gateway locations. For users with GeoPandas experience who want to make their own GeoDataFrame, go to [the first subsection](#users-with-geopandas-experience). For users without GeoPandas experience or want step-by-step instructions, go to [the second subsection](#users-without-geopandas-experience).
##### Users with GeoPandas Experience
Create a GeoDataFrame with point geometry. There should be an entry for each potential gateway location. Optionally, add an "altitude" column that contains the height for each gateway location (for USGS DSMs the height above sea level in meters), or NaN for values to be filled by DSM. If no "altitude" column is present all values will be filled by DSM. Optionally, add a "built" column that contains `0` for gateways that have not been built or `1` for gateways that are already built. If no "built" column is present all gateways will be assumed to be unbuilt. **Make sure the GeoDataFrame has a coordinate reference system**. Write the GeoDataFrame to a geojson file.

If you had any NaNs in the altitude column (or no altitude column at all) you must fill them. There is a helper script for this if you already have a [DSM](#dsm-creation). In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/manual_fac.py dsm_path gdf_path output_path` where `dsm_path` is a path to the dsm file on your computer, `gdf_path` is a path to the geojson file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes.

##### Users without GeoPandas Experience
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

In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/manual_fac.py dsm_path csv_path output_path` where `dsm_path` is a path to the dsm file on your computer, `csv_path` is a path to the csv file on your computer, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes.

#### Hybrid Gateway Placement
This section will show you how to combine [building corner](#gateways-from-building-corners) and [manually placed](#manual-gateway-placement) gateways. It requires you to have already created geojson files for both building corners and manually placed gateways. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/hybrid_fac.py corner_path manual_path output_path` where `corner_path` is a path to the building corner geojson, `manual_path` is a path to the manual gateway geojson, and `output_path` is a path to the new file to be created ending in ".geojson". **Note:** If any paths contain a space, that path should be wrapped in double quotes.

*By default, the model will assume that building corners are inexact because not all building owners are willing to house a gateway. Conversely, the model will assume that all manual gateway locations are exact. For inexact locations, the model will suggest an area that would be a good choice for a gateway. You can break either assumption by adding* `all_exact` *or* `no_exact` *as an additional argument, respectively.*

### Training a Model
This section will describe how to train a model for your municipality. If you want to collect data for a more accurate model, go to the [Custom Model](#custom-model). If you do not want to use resources to collect data, go to [Premade Model](#premade-model).

#### Premade Model
This section will show you how to set up model files without needing to collect extra data.

##### Training from Premade Data
This section will show how to train a model using data precollected from Ithaca and Brooklyn. First, go to [this Box folder](https://cornell.box.com/s/mh3mfpg478jld3hdprkx9js9hnbe921n) and download the precollected data from each desired city. Make sure that you download both the "X" and the "y" file for each city you would like to use. Place the downloaded files in a folder, **DO NOT CHANGE THEIR NAMES**. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/train_premade_model.py folder_path brooklyn,ithaca xg_out` where `folder_path` is a path to the folder containing the downloaded data files and `xg_out` is the desired path to the resulting model file, ending in ".json". You can replace `brooklyn,ithaca` with a different comma-separated (no spaces) list of the cities for which data was collected. The names must correspond exactly with the names of the data in the folder. To train a model with only one city's data, just write that city (for example, `brooklyn` without any commas).

##### Creating a Standard Scaler
This section will show how to create a standard scaler for your municipality. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/estimate_sc.py dsm_path demands_path potential_gateways_path sc_out link_target` where `dsm_path` is the path to the [DSM](#dsm-creation) on your computer, `demands_path` is the path to the demand geojson file created in [Creating Coverage Area](#creating-coverage-area), `potential_gateways_path` is the path to the potential gateway geojson file created in [Finding Potential Gateways](#finding-potential-gateways), `sc_out` is the desired output path for the resulting standard scaler file with a ".onnx" file extension, and `link_target` is an integer greater than or equal to `1`. The `link_target` parameter roughly controls the accuracy of the resulting scaler, with a larger integer being more accurate but slower to compute. Every unit of increase in the `link_target` parameter increases the computation time roughly by the number of potential gateways. The output standard scaler file will be placed at the `sc_out` path. You can move or rename the file, but make sure it keeps the ".onnx" extension and remember where it is kept.

#### Custom Model
This section will show you how to train a model using collected data. A custom model is not necessary, but will likely lead to more accurate results. Model training requires building some gateways around your city and collecting data using transmitters. This section is intended for a semi-technical audience.

##### Data Collection
This section is under construction. It will describe how to collect the data necessary to train a model.

##### Training Data Format
Training data consists of a GeoPandas [GeoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html) with Shapely [LineString](https://shapely.readthedocs.io/en/stable/reference/shapely.LineString.html) geometry. The first point of the LineString should be the location of the transmission. The second point of the LineString should be the location of the gateway. There should be columns `ele_tr` and `ele_gw` that give the elevations of the transmission and gateway, respectively (in the same units as the DSM, which is meters above sea level for USGS DSMs). There should be a `success` column that is `1` if the transmission was successful, and `0` otherwise. The GeoDataFrame should have a set CRS (otherwise it will be assumed to be [EPSG:4326](https://epsg.io/4326)). Save the training data file to your filesystem as a geojson in this format.

##### Make the Training Data
In this section you will create training inputs and outputs for model training. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/make_train_data.py dsm_path train_data_path x_out_path y_out_path` where `dsm_path` is a path to the dsm file on your computer, `train_data_path` is a path to the training data file on your computer, `x_out` is the desired path for the created training inputs with the ".npy" extension, and `y_out` is the desired path for the created training outputs with the ".npy" extension. While computing, the program will print its progress after processing every 512 links, so do not be alarmed if the progress stays on `1` for a while. This task will likely take a while. The command will output files to the `x_out` and `y_out` paths, make sure to remember these paths for training. We will refer to the files as "X file" and "y file", respectively.

##### Training the Prediction Model
In this section you will use the X and y files from [above](#make-the-training-data) to train a prediction model. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/train_model.py X_path y_path sc_out xg_out 0.0` where `X_path` is a path to the X file on your computer, `y_path` is a path to the y file on your computer, `sc_out` is the desired path for the model standard scaler on your computer ending in ".onnx", and `xg_out` is the desired path for the model on your computer ending in ".json". You can also change `0.0` to any float in `[0.0, 1.0)` to designate a testing set. This defines a proportion of the data to set aside and test the resulting model on. The [Brier score](https://en.wikipedia.org/wiki/Brier_score) (lower is better) will be printed after the model trains if the proportion is greater than `0.0` (the proportion must be high enough that at least one element is in the testing set). You can move and rename the standard scaler and xg files, but be sure to keep the same extensions.

### Making Predictions
In this section you will use the model created in [Training a Model](#training-a-model) to generate predictions for how much coverage potential gateways provide. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/make_predictions.py dsm_path demands_path potential_gateways_path sc_path xg_path out_path` where `dsm_path` is the path to the [DSM](#dsm-creation) on your computer, `demands_path` is the path to the demand geojson file created in [Creating Coverage Area](#creating-coverage-area), `potential_gateways_path` is the path to the potential gateway geojson file created in [Finding Potential Gateways](#finding-potential-gateways), `sc_path` is the path to the ".onnx" standard scaler file created in [Training a Model](#training-a-model), `xg_path` is the path to the ".json" model created in [Training a Model](#training-a-model), and `out_path` is the desired path to the new prediction file, ending in ".npy". You can move and rename the prediction file, but be sure to keep the ".npy" extension.

### Performing Optimization
In this section you will use the prediction file generated in [Making Predictions](#making-predictions) to determine the best placement of gateways. There are two optimization modes outlined in the following sections. The first mode takes a [budget](#fixed-budget) (i.e. a number of gateways) and places those gateways to maximize coverage. The second mode takes a [desired coverage](#target-coverage) and places gateways to try to achieve that coverage as cheaply as possible.

#### Fixed Budget
In this section you will provide a fixed target budget and the tool will find the best placement of gateways to maximize coverage without exceeding the budget. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/maximize_coverage.py demands_path potential_gateways_path predictions_path out_path budget` where `demands_path` is the path to the demand geojson file created in [Creating Coverage Area](#creating-coverage-area), `potential_gateways_path` is the path to the potential gateway geojson file created in [Finding Potential Gateways](#finding-potential-gateways), `predictions_path` is a path to the predictions file created in [Making Predictions](#making-predictions), `out_path` is the desired path to the file containing the solution ending in ".json", and `budget` is the cost to stay under (in number of gateways). 

For advanced users: you can customize the cost of the potential gateway locations by providing a `cost` column in the GeoDataFrame, otherwise the cost for all gateways is assumed to be `1`.

#### Target Coverage
In this section you will provide a desired coverage amount and the tool will find the cheapest placement of gateways that achieves that coverage. In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/minimize_budget.py dem_file fac_file prr_file out_file coverage` where `demands_path` is the path to the demand geojson file created in [Creating Coverage Area](#creating-coverage-area), `potential_gateways_path` is the path to the potential gateway geojson file created in [Finding Potential Gateways](#finding-potential-gateways), `predictions_path` is a path to the predictions file created in [Making Predictions](#making-predictions), `out_path` is the desired path to the file containing the solution ending in ".json", and `coverage` is a decimal in the range [0.0, 1.0) representing the desired target coverage. This represents the probability that a given transmission is received (0.5 means that half of all transmissions are received; if a transmitter sent a packet every hour for a day under `0.5` coverage then there is about `99.999994%` chance at least one of the packets is received). 

For advanced users: you can customize the cost of the potential gateway locations by providing a `cost` column in the GeoDataFrame, otherwise the cost for all gateways is assumed to be `1`. You can also customize the amount of desired coverage on a per-point basis by providing a `coverage` column in the demands GeoDataFrame and omitting the last argument to the command.

### Viewing Results
In this section you will plot the coverage provided by a solution file generated in [Performing Optimization](#performing-optimization). In the command prompt, ensure that you are in the correct directory and have the environment activated (steps 4. and 6. of the [non-python user instructions](#non-python-users)). Then, run `python scripts/plot_coverage.py demands_path potential_gateways_path predictions_path solution_path` where `demands_path` is the path to the demand geojson file created in [Creating Coverage Area](#creating-coverage-area), `potential_gateways_path` is the path to the potential gateway geojson file created in [Finding Potential Gateways](#finding-potential-gateways), `predictions_path` is a path to the predictions file created in [Making Predictions](#making-predictions), `solution_path` is the path to the solution file created in [Performing Optimization](#performing-optimization). This will cause a window to pop up showing the coverage. Optionally, you can put another path ending in ".png" as an additional argument and the plot will be placed at that location as an image file instead.

## Acknowledgement
The development of these tools was supported by the NSF under grant CNS-1952063.
