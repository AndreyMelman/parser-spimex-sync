from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

BASE_URL = "https://spimex.com/markets/oil_products/trades/results/"
DOWNLOAD_DIR = "downloads/"
TARGET_DATE = datetime(2023, 1, 1)