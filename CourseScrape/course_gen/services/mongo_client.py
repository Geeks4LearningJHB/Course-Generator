from pymongo import MongoClient
import os

class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(
                os.getenv("MONGO_URI", "mongodb://mongo:27017/")
            )
            cls._instance.db = cls._instance.client["educational_content"]
        return cls._instance
    
    def get_collection(self, collection_name="generated_courses"):
        return self.db[collection_name]