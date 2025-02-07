# 🚄 Geospatial Train Tracking & Delay Analysis
![Project Visual](/docs/images/folium_popup_map.png)

**Credit:** This project was only possible thanks to Realtime Trains API!

## 📌 Project Overview
This project analyzes train delays at **Finsbury Park (FPK)**, capturing **all arriving trains**, regardless of their origin. The project uses **FastAPI, PostgreSQL, SQLAlchemy, Pandas, and AsyncSession** for efficient database operations. Additionally, it includes **geospatial mapping with Folium & GeoPandas**.

## 📂 Project Structure
```
/train-tracking
│── main.py                # 🔄 Runs the full data pipeline & API
│── config.py              # 🛠️ Stores API credentials & configurations
│
│
├── data_pipeline/         # 🌐 Data processing scripts
│   ├── extract.py         # 📀 Extracts arrivals from RTT API (past 7 days)
│   ├── clean.py           # 🌱 Cleans & processes data (calculates delays, adjusts dates)
|   |── merge.py           # 🔄 Merges train arrival and station geospatial data 
|   |── map.py         # Creates interactive maps using merged data 
│   └── utils.py           # 🏢 Uploads processed data to PostgreSQL
│
├── db/                    # 📁 Database setup & schema
│   ├── db_main.py         # 🔧 Manages database connection
│   ├── db_schema.py       # 📚 Defines SQLAlchemy models (includes origin/destination CRS)
│   └── db_init.py         # 🛠️ Initialises PostgreSQL tables
│
├── geospatial/            # 🛠️ Geospatial mapping code
│   ├── get_spatial_data.py  # Downloads & processes station geospatial data
│   └── mapping.py         # Creates interactive maps using merged data 
│
├── data/                  # 🛠️ Extracted geospatial data from doogal.co.uk
│   ├── station_data.json  # Raw station data in JSON format 
│   └── station_coordinates.csv  # Processed station coordinates 
│
├── maps/               # 🛠️ Generated train maps 
│   └── train_delays_maps.html  # Interactive map with delay info
│
├── services/              # 🛠️ API interaction scripts
│   └── trains_main.py     # 🚃 Fetches arrival data & structures JSON
│
├── sql/                   # 📈 SQL Optimization Scripts
│   ├── 01_create_partition.sql  # 📊 Partitioning tables by date
│   ├── 02_create_indexes.sql    # ⚖️ Indexing to speed up queries
│   ├── 03_slow_vs_fast_queries.sql  # 🔢 Performance benchmarking
│   └── 04_results.md      # 📘 Performance improvement docs
│
├── outputs/               # 📅 Data storage for RTT data
│   ├── raw_data_FPK_YYYY-MM-DD.json  # 📝 Unfiltered API responses
│   ├── cleaned_data.csv   # 📈 Processed train data
│   └── missing_actual_arrivals.csv   # ⚠️ Records with missing actual arrival times
│
├── docs/                  # 📖 Detailed documentation
│   ├── 00_project_setup.md  
│   ├── 01_db_setup.md 
│   ├── 02_db_optimisation_results.md   # 📘 Performance improvement docs
│   ├── 03_geo_setup.md  
│   └── 04_merge_datasets.md  
│
├── environment.yml        # 🛠️ Conda environment setup
│
└── README.md              # 📗 Project documentation
```

## ⚙️ Setting Up the Environment
I chose:
- conda virtual environment
- storing variables in `.env` doc 

For details, see [Project Setup](/docs/00_project_setup.md)

For environemnt dependencies, see [Environment Dependecies](environment.yml)

## 🚀 Running the Train API & Data Pipeline
When the FastAPI server starts, it automatically **fetches and processes train arrival data for the past 7 days** (including adjusting dates for next-day arrivals) and uploads it to the database. If the database is empty, the server must be running to extract the initial data.

```bash
uvicorn main:app --reload
```

### 🏢 API Endpoints
| Endpoint | Description |
|--|--|
| `/api/station/FPK/date/2025-02-01` | Get arrivals at FPK for a specific date |
| `/` | Check if API is running |

## 📚 PostgreSQL Database Setup - revised on 4 February 
### 🔄 Data Model
| Column | Type | Description |
|--|--|--|
| `run_date` | DATE | Date of train arrival |
| `service_id` | STRING | Unique train ID |
| `operator` | STRING | Train company |
| `origin` | STRING | Departure station |
| `origin_crs` | STRING | Departure station code |
| `destination` | STRING | Arrival station |
| `destination_crs` | STRING | Arrival station code |
| `scheduled_arrival` | TIMESTAMP | Scheduled arrival time |
| `actual_arrival` | TIMESTAMP | Actual arrival time (if available) |
| `is_actual` | BOOLEAN | True if real arrival recorded |
| `delay_minutes` | INTEGER | Delay in minutes |
| `is_passenger_train` | BOOLEAN |	True if the train is a passenger service |
| `was_scheduled_to_stop` |	BOOLEAN	| True if the stop was originally scheduled |
| `stop_status`	| STRING |	Display status (e.g., "CALL") |

### 📈 Query Optimisation
- **Partitioning**: Splits tables by `run_date`
- **Indexing**: Speeds up searches on `run_date`, `destination`
- **Result**: Queries run **120x faster**!

For further details on database optimisation, see [DB Optimisation Documentation](/docs/02_db_optimise.md).
for sql scripts, see [SQL Queries](/sql_old_table).


## 🗺️ Geospatial Mapping
### Inputs:
- Train Arrival Data: outputs/cleaned_data.csv (includes station names) 🚆
- Station Geospatial Data: data/station_coordinates.csv (contains station names, their codes, latitude, and longitude) 📍

### Steps:
1. Verify Data Structure 🔍
2. Merge the Datasets 🔄 
3. Validate data: checking and fixing missing values. 
4. Update the Schema and Reinitialize the Database 🛠️
5. Update Mapping: Use the merged dataset for visualising train delays and station locations 🗺️
6. In Progress: Visualising delay hotspots 🔥

Troubleshooting:
We have 292 missing values for origin stations and 281 for destination stations:

![Missing Values](/docs/images/03_missing_values.png)

The affected stations were London Kings Cross (over 200 records), Letchworth (over 40), and one mismatched record for `Peterboro Maint Shed Gbrf`.

After fixing this, the map has not more empty popup markers fro Kings Cross or Letchworth! 

For a detailed guide on geospatial setup, refer to [Geospatial Data Setup Guide](/docs/03_geo_setup.md) and [Adding Delays Data Guide](/docs/04_merge_delays.md).

## 📺 Next Steps
- **Performance Dashboards**: Operator performance analysis
- **CI/CD Pipelines**: Automate deployment with Docker & GitHub Actions

## 📢 Disclaimer
Realtime Trains API data is for **non-commercial use only** and requires attribution.


---

### Notes on the Updates:
Update 5 February 2025
- Added scripts for data validation and cleaning of mismatched station names between two datasets 
- Correctly matched station names in RTT and Doogal data merge 
- Dropped unnecessary values such as for  Peterboro Maintenance Shed

Update 4 February 2025
- Added folders for merged datasets.
- Updated databse scheme to include `origin_crs` and `destination_crs`.
- Corrected delay calculation logic in the ETL process to handle next-day arrivals properly. 

Update 3 February 2025
- Revised project structureto include updated names and descriptions.
- Enhanced ETL process to automatically adjust dates for next-day arrivals. 


The "Running the Train API & Data Pipeline" section notes that the project automatically processes data (including date adjustments for next-day arrivals).