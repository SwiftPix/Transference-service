import os

class Settings:
    def __init__(self):
        self.ENVIROMENT = os.getenv("ENVIROMENT", "test")
        self.MONGO_DATABASE_URI = os.getenv("MONGO_DATABASE_URI", "mongodb://localhost:27017")
        self.MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "test")
        self.USER_API = os.getenv("USER_API", "http://0.0.0.0:5000")
        self.GEOLOC_API = os.getenv("GEOLOC_API", "http://0.0.0.0:5000")

settings = Settings()
