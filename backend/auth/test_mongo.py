from auth.mongo_models import users_collection

users_collection.insert_one(
    {
        "username": "testuser",
        "password": "123456"
    }
)

print("Connected to MongoDB successfully")