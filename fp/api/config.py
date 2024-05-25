import os

from dotenv import load_dotenv

if os.path.exists("config.env"):
    load_dotenv(dotenv_path="config.env")

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ADRESS = os.getenv("DB_ADRESS")
DB_NAME = os.getenv("DB_NAME")
