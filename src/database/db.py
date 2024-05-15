from pymongo import MongoClient
from settings import settings

def initialize_mongo():
    mongo_uri = settings.MONGO_DATABASE_URI
    db_name = settings.MONGO_DATABASE_NAME

    client = MongoClient(mongo_uri)
    db = client[db_name]

    return db
