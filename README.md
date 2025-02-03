# 🚄 Geospatial Train Tracking & Delay Analysis

**Credit:** This project was only possible thanks to Realtime Trains API!

## 📌 Project Overview
This project analyzes train delays at **Finsbury Park (FPK)**, capturing **all arriving trains**, regardless of their origin. The project uses **FastAPI, PostgreSQL, SQLAlchemy, Pandas, and AsyncSession** for efficient database operations. Future updates will include **geospatial mapping with Folium & GeoPandas**.

## 📂 Project Structure
```
/train-tracking
│── main.py                # 🔄 Runs the full data pipeline & API
│── config.py              # 🛠️ Stores API credentials & configurations
│
├── data_pipeline/         # 🌐 Data processing scripts
│   │── extract.py         # 📀 Extracts arrivals from RTT API (past 7 days)
│   │── clean.py           # 🌱 Cleans & processes data (calculates delays, adjust dates)
│   │── utils.py           # 🏢 Uploads processed data to PostgreSQL
│
├── db/                    # 📁 Database setup & schema
│   │── db_main.py         # 🔧 Manages database connection
│   │── db_schema.py       # 📚 Defines SQLAlchemy models
│   │── db_init.py         # 🛠️ Initialises PostgreSQL tables
│
├── services/              # 🛠️ API interaction scripts
│   │── trains_main.py     # 🚃 Fetches arrival data & structures JSON
│
├── sql/                   # 📈 SQL Optimization Scripts
│   │── 01_create_partition.sql  # 📊 Partitioning tables by date
│   │── 02_create_indexes.sql    # ⚖️ Indexing to speed up queries
│   │── 03_slow_vs_fast_queries.sql  # 🔢 Performance benchmarking
│   │── 04_results.md   # 📘 Performance improvement docs
│
├── outputs/               # 📅 Data storage
│   │── raw_data_FPK_YYYY-MM-DD.json  # 📝 Unfiltered API responses
│   │── cleaned_data.csv   # 📈 Processed train data
│   │── missing_actual_arrivals.csv   # ⚠️ Trains with missing actual arrival times
│
├── environment.yml        # 🛠️ Conda environment setup
│
└── README.md              # 📗 Project documentation
```

## ⚙️ Setting Up the Environment
- Install **Miniconda**, create an isolated environment:
  ```bash
  conda create --name trains_env python=3.9
  conda env create -f environment.yml
  conda activate trains_env
  ```
- Add RTT API credentials to `.env`:
  ```bash
  RTT_USERNAME=<your_guess>
  RTT_PASSWORD=(another_guess>)
  RTT_ENDPOINT=<your_endpoint>
  ```
- Initialise the database:
  ```bash
  python db/db_init.py
  ```

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

## 📚 PostgreSQL Database Setup
### 🔄 Data Model
| Column | Type | Description |
|--|--|--|
| `run_date` | DATE | Adjusted date of train arrival |
| `non_adjusted_date` | DATE | Original date as provided by the RTT API |
| `service_id` | STRING | Unique train ID |
| `operator` | STRING | Train company |
| `origin` | STRING | Departure station |
| `destination` | STRING | Arrival station |
| `scheduled_arrival` | TIMESTAMP | Scheduled arrival time |
| `actual_arrival` | TIMESTAMP | Actual arrival time (if available) |
| `is_actual` | BOOLEAN | True if real arrival recorded |
| `delay_minutes` | INTEGER | Delay in minutes |
| `is_passenger_train` | BOOLEAN |	True if the train is a passenger service |
|  `next_day_arrival`	| BOOLEAN |	True if the arrival occurs after midnight |
| `was_scheduled_to_stop` |	BOOLEAN	| True if the stop was originally scheduled |
| `stop_status`	| STRING |	Display status (e.g., "CALL") |

### 📈 Query Optimisation
- **Partitioning**: Splits tables by `run_date`
- **Indexing**: Speeds up searches on `run_date`, `destination`
- **Result**: Queries run **120x faster**!

## 📺 Next Steps
- **Geospatial Mapping**: Visualising delay hotspots with Folium & GeoPandas
- **Performance Dashboards**: Operator performance analysis
- **CI/CD Pipelines**: Automate deployment with Docker & GitHub Actions

## 📢 Disclaimer
Realtime Trains API data is for **non-commercial use only** and requires attribution.


---

### Notes on the Updates:
- **Project Structure:**  
  The structure now includes updated names and descriptions reflecting the new database fields and the adjusted ETL process.
  
- **Database Schema:**  
  The Data Model section now includes `non_adjusted_date` (storing the original API date) alongside `run_date` (the adjusted date).

- **ETL Process:**  
  The "Running the Train API & Data Pipeline" section notes that the project automatically processes data (including date adjustments for next-day arrivals).
