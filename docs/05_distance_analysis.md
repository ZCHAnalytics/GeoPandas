# Spatial analysis with GeoPandas and Shapely


1. Add dependences

pip install geopandas


To compute the distance between stations, we'll follow these steps:

1. Prepare Data:

- Ensure that the station data contains the latitude and longitude for each station.
- Convert the station data into a GeoDataFrame using GeoPandas, which will allow us to perform spatial operations like calculating distances.
- Convert Coordinates to GeoDataFrame:
- Convert the station latitude and longitude into a geometry column using GeoPandas' Point objects. # allows the use of GeoPandas' spatial methods, including distance calculations.
- Calculate Distances:

Once the data is in a GeoDataFrame, we can compute the distances between stations using GeoPandas' distance function.

We can compute distances from Finsbury Park to other stations and identify which stations are the nearest.

