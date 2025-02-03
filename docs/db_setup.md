db_setup.md
# Database Setup Guide 

## DB Folder Overview:
the `db/` folder contains the following files:
- **`db_main.py`**  - Handles database connection 
- **`db_schema_alchemy.py`** - Defines SQLAlchemy models 
- **`db_init.py`** - Used for initialising the database 
- **`sql_script.sql`** - Raw commands for database setup 


## 📌 1. Install Dependencies

FastAPI interactgs with PostgreSQL using the following dependencies:
```bash
pip install sqlalchemy asyncpg
```

Additionally, install `psycopg2` (PostgreSQL adapter for Python):
```bash
conda install psycopg2
```
PostgreSQL Installation

![alt text](images_db/image-3.png)

## 🗄 2. Create the Database
🔹 Step 1: Open pgAdmin or PostgreSQL Shell
Run the following command:
```bash
psql -U postgres
```
(Enter PostgreSQL user password when prompted)

🔹 Step 2: Create Database & User
Create a database for train tracking:
```sql
CREATE DATABASE trains_db;
```

Check if database exists
```sql
\l
``` 
Databse list:
![alt text](images_db/image-1.png)


Create a dedicated user:
```sql
CREATE USER trains_user WITH ENCRYPTED PASSWORD 'password';
```
Expected output: 
```
CREATE ROLE
```
Grant all privileges to the new user:
```sql
GRANT ALL PRIVILEGES ON DATABASE trains_db TO trains_user;
```

Exepcted output: 
```
GRANT
```
Exit the PostgreSQL shell:
```sql
\q
```

## 🔧 3. Configure Database Connection
Add database credentials to `.env` file 
```
DATABASE_URL=postgresql+asyncpg://trains_user:password@localhost/trains_db
```

## 📜 4. Define Database Schema using **SQLAlchemy** 
Create the schema file:
```bash
touch db_schema_alchemy.py
```

## 🔗 5. Connect to the Database
```bash
psql -U postgres -d trains_db
```

Connected Database:
 
 ![alt text](images_db/image-4.png)

Check database table structure:
```sql
\d train_tracking
```

List all tables:
```sql
\dt
```

Database tables:

![alt text](images_db/image-5.png)

## 🚀 6. Integrate Database with FastAPI

To use the database inside FastAPI, update `db_main.py`:

```bash
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create asyn database engine
engine = create_async_engine(DATABASE_URL, future=True)

# Create async session factory 
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session
```