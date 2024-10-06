import os
import certifi
from pymongo import MongoClient
import dotenv

# Load env variables
dotenv.load_dotenv()

# MongoDB configuration
MONGODB_URI = os.getenv("MONGO_CLIENT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

# # Debug prints to check env variables
# print(f"MONGO_CLIENT: {MONGODB_URI}")
# print(f"DATABASE_NAME: {DATABASE_NAME}")
# print(f"COLLECTION_NAME: {COLLECTION_NAME}")
# print(f"INDEX_NAME: {INDEX_NAME}")

# # Check if DATABASE_NAME is a string
# if not isinstance(DATABASE_NAME, str):
#     raise TypeError("DATABASE_NAME must be an instance of str")

# MongoDB Connection
ca_cert_path = certifi.where()
client = MongoClient(MONGODB_URI, tlsCAFile=ca_cert_path)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def get_collection(collection_name):
    return db[collection_name]


# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Print database names to verify connection
try:
    for db_name in client.list_database_names():
        print(db_name)
except Exception as e:
    print(f"An error occurred while listing databases: {e}")
