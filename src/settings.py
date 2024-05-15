import os

class Settings:
    def __init__(self):
        self.ENVIROMENT = os.getenv("ENVIROMENT", "dev")
        self.MONGO_DATABASE_URI = os.getenv("MONGO_DATABASE_URI", "mongodb://localhost:27017")
        self.MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "transferenceDB")

settings = Settings()
