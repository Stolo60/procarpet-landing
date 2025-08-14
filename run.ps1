# Windows PowerShell launcher
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
mkdir -Force public | Out-Null
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
