from pymongo import MongoClient
from pymongo.collection import Collection


class MongoDBManager:
    CONNECTIONS = {}
    CONNECTION_COUNT = 0

    def __init__(
        self,
        mongodb_uri: str,
        db_name: str,
        collection_name: str,
        soft_delete: bool = True,
        **kwargs,
    ):
        if mongodb_uri not in MongoDBManager.CONNECTIONS:
            MongoDBManager.CONNECTIONS[mongodb_uri] = MongoClient(mongodb_uri, **kwargs)
            MongoDBManager.CONNECTION_COUNT += 1
        self.client = MongoDBManager.CONNECTIONS[mongodb_uri]
        self._check_duplicated_db_name(db_name)
        self.db = self.client.get_database(db_name)
        self.collection: Collection = self.db.get_collection(collection_name)
        self.soft_delete = soft_delete

    def _check_duplicated_db_name(self, db_name):
        dbs = {o.lower(): o for o in self.client.list_database_names()}
        if db_name.lower() in dbs and dbs[db_name.lower()] != db_name:
            raise Exception(
                f"""Current DB_NAME <{db_name}> duplicated with already existed DB_NAME: <{dbs[db_name.lower()]}>"""
            )