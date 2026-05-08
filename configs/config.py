import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL: str = os.getenv("BASE_URL", "https://jsonplaceholder.typicode.com")
    TIMEOUT: int = int(os.getenv("TIMEOUT", 10))
    RETRIES: int = int(os.getenv("RETRIES", 3))
    API_KEY: str | None = os.getenv("API_KEY")


config = Config()
