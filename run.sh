#!/usr/bin/env bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p public
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
