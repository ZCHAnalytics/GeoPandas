db_setup.md

# 🚄 PostgreSQL Database Setup for Train Tracking
## 📌 1. Install Dependencies
I use PostgreSQL with FastAPI using the following dependencies:

`pip install sqlalchemy asyncpg alembic`

![alt text](images_db/image-2.png)

Additionally, install `psycopg2` (PostgreSQL adapter for Python):
`conda install psycopg2`

![alt text](images_db/image-3.png)

## 🗄 2. Create the Database
🔹 Step 1: Open pgAdmin or PostgreSQL Shell
Run the following command in your terminal:

`psql -U posgres` and enter password 

🔹 Step 2: Create Database & User
Create a database for train tracking:

`CREATE DATABASE trains_db;`
Check if database exists
`\l` 

![alt text](images_db/image-1.png)


Create a dedicated user:
`CREATE USER trains_user WITH ENCRYPTED PASSWORD 'password';`

output: CREATE ROLE

`GRANT ALL PRIVILEGES ON DATABASE trains_db TO trains_user;`

output: GRANT

`\q` # exit psql shell 

## 🔧 3. Configure Database Connection
Create a database connection file:
`touch database.py`
Add db credentials to `.env` file 

## 📜 4. Define Database Schema using **SQLAlchemy** and **Pydantic**
`touch schema.py`
`touch db_schema.py`

## 🔗 5. Connect to the Database

`psql -U postgres -d trains_db`
 
 ![alt text](images_db/image-4.png)

Check database table structure:
`\d train_tracking`

List all tables:
`\dt`


![alt text](images_db/image-5.png)

## 🚀 6. Add Database Dependency to FastAPI
Finally, update `db_main.py` to provide a database session to FastAPI routes.