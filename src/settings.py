import os

class Settings:
    def __init__(self):
        self.ENVIROMENT = os.getenv("ENVIROMENT", "dev")
        self.MONGO_DATABASE_URI = os.getenv("MONGO_DATABASE_URI", "mongodb://localhost:27017")
        self.MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "transference-dev")
        self.USER_API = os.getenv("USER_API", "http://0.0.0.0:5000")
        self.GEOLOC_API = os.getenv("GEOLOC_API", "http://0.0.0.0:5000")
        self.ACCOUNT_SID = os.getenv("ACCOUNT_SID", "123")
        self.AUTH_TOKEN = os.getenv("AUTH_TOKEN", "123")

settings = Settings()
