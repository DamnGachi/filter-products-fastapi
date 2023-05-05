import sys
import pymongo


uri = "mongodb+srv://admin:admin@dastish.gf1hbe3.mongodb.net/?retryWrites=true&w=majority"
try:
    client = pymongo.MongoClient(uri)
    print("success")

except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)


db = client.myDatabase
my_collection = db["eggs"]