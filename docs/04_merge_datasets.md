# Merging Datasets Guide


missing CRS column in cleaned_data.csv:

![Missing CRS Column](/docs/images/04_missing_crs_column.png)


Lets check the realtime Train APi Documentation on how to retrieve CRS data:

![RTT Api Key](/docs/images/04_rtt_api_key.png)
 - it does not offer station codes for origin or destination stations 


 check the doogle 
 - it does offer station codes for all stations and our script already retrieves crs and station names. 


- amend 
- amend  

What This Script Does:
Loads the Two Datasets:
Reads the train arrival data and the station coordinates data into separate DataFrames.

Merges the DataFrames:
It uses a left merge on the crs column so that every record in train arrival data is preserved, with matching station coordinates added.

Saves the Merged Data:
The merged DataFrame is saved as a CSV file for later use.

## Step 3: Run and Verify the Merge
```bash
python integrate_data.py
```

Running the command gives this output:
![Terminal Output Merge](/docs/images/04_merge_output.png)

- columns from both the train arrival data and the station coordinates
-  file outputs/merged_train_station_data.csv has been created and contains the merged data

Here how it looks:
![Merged_Dataset](/docs/images/04_merged_dataset.png)

## Step 4: Update mapping Script to Use the Merged Data

- create new folder for geodata at the root 


![Output for new mapping](/docs/images/04_output_remapping.png)

## Step 5: Test mapping.py 
```bash
python geospatial/mapping.py
```

#TODO
Troubleshotting

Wrong delay_mionutes calculated:
![Wrong delay_calculation](/docs/images/04_wrong_delay_calculation.png)


Mistake in clean.py file:

Fixed now! 
![Fixed Marker with Correct Delay Calculaiton](/docs/images/04_fixed_delay_marker.png)