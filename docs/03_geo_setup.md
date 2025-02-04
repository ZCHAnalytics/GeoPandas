# Geospatial Setup Guide

## 1. Instal Required Libraries
To work with geospatial data and create interactive maps, we need to install additional libraries:
- **GeoPandas** - for creating and manipulating geospatial data objects. 
- **Shapely** - for constructing and operating on geometric objects.  
- **Folium** - for building interactive web maps.   

Install these libraries using:
```bash
pip install geopandas shapely folium
```
#TODO
Add new dependencies to `environment.yml` file

## 2. Create Mapping file for Finsbury Park coordinatres
Create a new file (e.g., geospatial/mapping.py) to define a base map centered on Finsbury Park. This file will:

- Set up the base map using Folium.
- Plot markers (and later, additional layers) for train stations.

## 3. Retrieve Publicly available data of UK rail stations 
To map station locations, obtain a dataset containing the geographic coordinates of UK rail stations. For example:

- Visit Doogal to download station data in JSON, GeoJSON, or CSV format.
- This dataset should include key columns such as:
    - CRS code (e.g., "code")
    - Station name (e.g., "name")
    - Longitude and Latitude

Create a script (e.g., geospatial/get_spatial_data.py) to download and process this data, ensuring we extract and save a CSV (e.g., data/station_coordinates.csv) with the required columns.

## 4. Merge Datasets and Visualise Geospatial Data
We have now: 

**Train Arrival Data**: outputs/cleaned_data.csv (which includes train arrival details and station identifiers)
**Station Geospatial Data**: data/station_coordinates.csv (with CRS, station names, latitude, and longitude)

Follow these steps:

- Verify Data Structure: Ensure both input files have consistent station identifiers. Currently, both files have "name" column. In the future, we need to check if Doogal names correspond to names on Realtime Trains API. 
- Merge the Datasets: Write a script (e.g., integrate_data.py) to merge the two datasets on the common identifier. 
- Update the Mapping Script: Modify geospatial/mapping.py to load and visualise data from the merged dataset, allowing to display train delays and station locations on the map.


#TODO
Troubleshooting steps:

![Empty Popup](/docs/images/03_empty_popup.png)