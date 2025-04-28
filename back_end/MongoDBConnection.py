from pymongo import MongoClient
import pymongo
from dataset import recipes_list

# Replace with your actual MongoDB Atlas URI
MONGO_URI = "mongodb+srv://test_user:IQ2he1ZHq3mkLJNX@cluster0.cogqyqp.mongodb.net/"

# Connect to MongoDB Atlas
# client = MongoClient(MONGO_URI)
client = pymongo.MongoClient(
    MONGO_URI,
    connectTimeoutMS=300000000,  # increase if needed
    socketTimeoutMS=300000000,
    retryWrites=True,
    tls=True
)

# Access your database and collection
db = client['recipe_database']             # You can name it whatever
collection = db['recipes']                 # Name of the collection

def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# Insert in batches of 100
batch_size = 100
total_inserted = 0

for batch in chunks(recipes_list, batch_size):
    collection.insert_many(batch)
    total_inserted += len(batch)

print(f"Inserted {total_inserted} recipes into MongoDB Atlas.")
