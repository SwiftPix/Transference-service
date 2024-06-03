import pymongo

from bson.objectid import ObjectId
from settings import settings
from utils.index import default_datetime

db_client = pymongo.MongoClient(settings.MONGO_DATABASE_URI)
db = db_client.get_database(settings.MONGO_DATABASE_NAME)

class PixKey:
    def __init__(self, type, key, user_id):
        self.type = type
        self.key = key
        self.user_id = user_id

    def save(self):
        pix_key = {
            "type": self.type,
            "key": self.key,
            "user_id": self.user_id,
            "created_at": default_datetime(),
            "updated_at": default_datetime(),
        }
        result = db.keys.insert_one(pix_key)
        return result.inserted_id
    
    def find():
        result = db.keys.find({})
        return result
    
    def find_by_user_id(user_id):
        result = db.keys.find({"user_id": user_id})
        return result
    
    def find_by_id(key_id):
        result = db.users.find({"_id": ObjectId(key_id)})
        key = next(result, None)
        return key
    