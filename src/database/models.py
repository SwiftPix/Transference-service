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
        result = db.keys.find({"_id": ObjectId(key_id)})
        key = next(result, None)
        return key
    
    def find_by_key(key):
        result = db.keys.find({"key": key})
        key = next(result, None)
        return key

class Transaction:
    def __init__(self, user_id, sender ,receiver_key, currency, value, type):
        self.user_id = user_id
        self.sender = sender
        self.receiver_key = receiver_key
        self.currency = currency
        self.value = value
        self.type = type

    def save(self):
        transaction = {
            "user_id": self.user_id,
            "sender": self.sender,
            "receiver_key": self.receiver_key,
            "currency": self.currency,
            "value": self.value,
            "type": self.type,
            "created_at": default_datetime(),
            "updated_at": default_datetime(),
        }
        result = db.transactions.insert_one(transaction)
        return result.inserted_id
    
    def find():
        result = db.transactions.find({})
        return result
    
    def find_by_id(transaction_id):
        result = db.transactions.find({"_id": ObjectId(transaction_id)})
        transaction = next(result, None)
        return transaction
    
    def find_by_user_id(user_id):
        result = db.transactions.find({"user_id": user_id})
        return result