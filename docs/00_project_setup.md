# 🚄 Project Setup Guide  

## 📂 1️⃣ Create Project Directory  

```bash
mkdir geopandas && cd geopandas
```
## 🛠 2️⃣ Initialize GitHub Repository  
```bash 
git init
git remote add origin <link to GitHub repository>
```

![Git Init](/docs/images/01_git_init.png)

## 🏗 3️⃣ Set Up Conda Virtual Environment

🔹 Install Miniconda
Download & install Miniconda from:
👉 Miniconda Installation Guide at: https://docs.anaconda.com/miniconda/install/

![Conda Install](docs/images/01_conda_install.png)

🔹 Verify Installation (Recommended)
Check the hash matches the one at: https://repo.anaconda.com/miniconda/ 

![Hash Check](docs/images/01_hash_check.png)

🔹 Initialize Conda in Git Bash
```bash 
C:/Users/zulfi/miniconda3/Scripts/conda init bash
```

![Conda Init Bash](docs/images/01_conda_init_bash.png)

🔹 Create & Activate Environment
```bash
conda create --name trains_env python=3.9 
conda activate trains_env
```
✅ This ensures all dependencies are installed in an isolated environment.

## 📦 4️⃣ Install Dependencies

```bash 
pip install fastapi uvicorn requests python-dotenv pandas matplotlib folium geopandas
```

## 🔑 5️⃣ Register for a Realtime Trains API Account

### ⚠ Important: 
- "Usage of this service is subject to a very simple clause. You must, at all times, credit Realtime Trains in any work that you create from this service. Beyond that, as long as you're not using the service for commercial purposes then use it to your heart's content!"

## 🚀 6️⃣ Test FastAPI
🔹 Create a test FastAPI application (`test_fastapi.py`)

```bash
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```    
🔹 Run FastAPI Server

```bash
uvicorn test_fastapi:app --reload
```
✅ If successful, the API should be running on http://127.0.0.1:8000/

![output_api](docs/images/01_output_api_test_call.png)

## 🔄 7️⃣ Test Connection to Realtime Trains API
🔹 Run the test script
```bash
python 01_api_call.py
```

🔹 Expected Output
✅ Retrieves API response keys and first key’s data

![API Call Keys](images/project_setup/01_api_call_keys.png)
