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

## 2. Retrieve Publicly available data of UK rail stations
To map station locations, obtain a dataset containing the geographic coordinates of UK rail stations. For example:

Visit Doogal to download station data in JSON, GeoJSON, or CSV format.
This dataset should include key columns such as:
- CRS code (e.g., "code")
- Station name (e.g., "name")
- Longitude and Latitude

Now, we create a script (e.g., geospatial/get_spatial_data.py) to download and process this data, ensuring we extract and save a CSV (e.g., data/station_coordinates.csv) with the required columns.
 
## 2. Check the compatability of datasets' structure

Our `cleaned_data.csv` misses information about CRS codes for origin and destination stations:

![Missing CRS Column](/docs/images/03_missing_crs_column.png)

Lets check the realtime Train APi Documentation on how to retrieve CRS data:

![RTT Api Key](/docs/images/03_rtt_api_key.png)

Their API does not offer station codes for origin or destination stations. 

## 3. Transform data to add missing CRS data for DataFrame that will be used for mapping

File `integrate_data.py`
What does the script does:
- load train arrival data `outputs/cleaned_data.csv` and station coordinates `data/station_coordinates.csv` and converts them into DataFrames
- creates temporaty DataFrame for origin stations that add coordinates info from Doogal data to the RTT data based on the name of origin station. Coordinates for station names not present in RTT data are discarded.  
- rename CRS and coordinates columns for origin stations from "crs" to "origin_crs", "latitude" to "origin_latitude", and "longitude" to "origin_longitude", to prepare for adding destination `crs`, `latitude`, and `longitude`.
- now we can add coordinates info from Doogal dataset to newly merged dataFrame based on the name of destination station. The rest of data from Doogal is discarded. 
- we should rename the new columnds in our merged dataFrame for consistency as "crs" to "destination_crs", "latitude" to "destination_latitude", and "longitude" to "destination_longitude"
- drop duplicated data 
- finally, save data as CSV file 

Without dropping columns, the station names are repeated twice:
![Without Dropping](/docs/images/03_without_dropping.png) 

After removing duplicate columns, our CSV output file looks neater:
![With Dropping](/docs/images/03_with_dropping.png) 

## 4. Validate Data 
Lets check if the merge retrieved Doogal data for all origin and destination listed in RTT file. 

So that we don't have empty popup markers:

![Empty Popup](/docs/images/03_empty_popup.png)

1️⃣ Use a Summary Table of Missing Values
Print a table showing missing values for key columns (origin_crs, destination_crs, origin_latitude, etc.).

We have 292 missing values for origin stations and 281 for destination stations:

![Missing Values](/docs/images/03_missing_values.png)

2️⃣ Filtered DataFrame
Save a CSV or screenshot where specific rows have missing values.
![Missing station values](/outputs/missing_station_values.csv)

3️⃣ Use a Heatmap or Bar Chart
Visualise missing values using tools like Matplotlib and Seaborn. 
Install seaborn and amend the script 

This will result in this output:
![Heat Map](/docs/images/03_heat_map.png)

✅ 4. Bar Chart of Missing Data Percentage
We still do not know how much of data is missing. We can use numpy to calculate percentages.  

We see that about 12 % od data is missing which is rather significant. 

![Percentage of Missing Values](/docs/images/03_percentage.png)


### Identify which stations has mismatch

using the script `values_check_agg.py`, we identify that the bulk of stations are London Kings Cross (over 200), Letchworth (over 40) and Peterboro Maint Shed Gbrf (1). 

![Stations Mismatch](/docs/images/03_mismatched_stations.png)

Since Peterboro Maint Shed is only mentioned once, and according to a closer inspection of `cleaned_data.csv` is not a passenger train, we can discard this record.
![Peterboro Maint Check](/docs/images/03_peterboro_check.png)


Check for other variations fo Kings Cross and Letchworth with Pandas string contains method.

None!:

![Names Variation Check](/docs/images/03_names_variation_check.png)

## 5. Fix missing values

✅ Create a Name Mapping Dictionary

we create a little map and repalced "London Kings Cross" with "King's Cross and "Letchwork" with "Letchworth Garden City" in the df_train.

When we run values_check.py again, the percentage of missing values went down to less than 1 %. Not bad!

![Reduced Percentage](/docs/images/03_reduced_percentage.png)

## 6. Drop unnecessary values

Since the station "Peterboro Maint" was not used by a passenger service, we don't need this record and will drop it. 

Amend the integrate_data.py file. 

Dropped and saved the record that results in an empty value:

![Dropped CSV](/docs/images/03_dropped_csv.png)

## 6. Generate Base Map
Create a new file (e.g., geospatial/mapping.py) to define a base map centered on Finsbury Park. This file will:

- Set up the base map using Folium.
- Plot markers for train stations.

All done! 
![Base Map](/docs/images/03_base_map.png)

The next step is to integrate delays data in our map.  