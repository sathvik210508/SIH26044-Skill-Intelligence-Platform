"""
SIH26044 — Platform Launcher Script
Initializes the SQLite database, seeds realistic demo accounts & data,
and runs the FastAPI server with the Single-Page Application on http://127.0.0.1:8000
"""

import sys
import os
import uvicorn

# Ensure backend directory is in pythonpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.database.db import Base, engine
from app.seed.seed_data import seed_database
from app.main import app

def main():
    print("=" * 70)
    print(" SIH26044: Real AI-Powered Skill Intelligence & Matching Platform")
    print("=" * 70)
    print("Initializing Database & Seeding Realistic Demo Records...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    print("Starting Web Server at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
