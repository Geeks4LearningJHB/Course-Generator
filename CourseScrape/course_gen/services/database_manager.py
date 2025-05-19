from course_gen.core.globals import (
    logging, pymongo, Dict, datetime, Optional, ObjectId, List, os, load_dotenv
)

load_dotenv()

class DatabaseManager:
    """MongoDB database manager for storing full course documents"""
    _instance = None
    _initialized = False

    # Singleton pattern for multiple DatabaseManager class initializations
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        print("MONGODB_COLLECTION_NAME:", os.getenv("MONGODB_COLLECTION_NAME"))
        
        try:
            connection_string = connection_string or os.getenv("MONGODB_CONNECTION_STRING")
            db_name = os.getenv("MONGODB_DATABASE_NAME", "CourseGenDB")  # Fallback to default
            collection_name = os.getenv("MONGODB_COLLECTION_NAME", "course")
            
            self.client = pymongo.MongoClient(connection_string)
            self.db = self.client[db_name]
            self.courses = self.db[collection_name]
            self.courses.create_index("title")
            
            if not self.__class__._initialized:
                logging.info("Connected to MongoDB successfully")
                self.__class__._initialized = True
        except Exception as e:
            logging.error(f"MongoDB connection error: {str(e)}")
            self.__class__._initialized = False
            raise

    def store_course(self, course_data: Dict) -> str:
        """Store a full course document including modules and units"""

        now = datetime.utcnow()

        course_doc = {
            "course_id": course_data.get("course_id", 1),
            "user_id": course_data.get("user_id", 1),
            "topic_id": course_data.get("topic_id", 1),
            "difficulty_id": course_data.get("difficulty_id", 1),
            "title": course_data["title"],
            "description": course_data["description"],
            "completion_time": course_data.get("completion_time", 40),
            "created_at": now,
            "updated_at": now,
            "modules": []
        }

        for i, module in enumerate(course_data.get("modules", []), start=1):
            module_doc = {
                "module_id": module.get("module_id", i),
                "module_order": module.get("module_order", i),
                "title": module["title"],
                "description": module.get("description", ""),
                "units": []
            }

            for j, unit in enumerate(module.get("units", []), start=1):
                unit_doc = {
                    "unit_id": unit.get("unit_id", j),
                    "unit_order": unit.get("unit_order", j),
                    "title": unit["title"],
                    "description": unit.get("description", ""),
                    "type": unit.get("type", "explanation"),
                    "body": unit.get("body", "")
                }
                module_doc["units"].append(unit_doc)

            course_doc["modules"].append(module_doc)

        result = self.courses.insert_one(course_doc)
        logging.info(f"Inserted course with ID: {result.inserted_id}")
        return str(result.inserted_id)

    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """Retrieve a full course document by its MongoDB ID"""
        course = self.courses.find_one({"_id": ObjectId(course_id)})
        if course:
            course["_id"] = str(course["_id"])
        return course

    def list_courses(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """List courses with pagination"""
        courses = list(self.courses.find().sort("created_at", -1).skip(offset).limit(limit))
        for course in courses:
            course["_id"] = str(course["_id"])
        return courses

    def search_courses(self, query: str) -> List[Dict]:
        """Search courses by title or description"""
        results = self.courses.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }).sort("created_at", -1)

        courses = []
        for course in results:
            course["_id"] = str(course["_id"])
            courses.append(course)
        return courses

    def update_course(self, course_id: str, update_data: Dict) -> bool:
        """Update a course document"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_course(self, course_id: str) -> bool:
        """Delete a full course document"""
        result = self.courses.delete_one({"_id": ObjectId(course_id)})
        return result.deleted_count > 0