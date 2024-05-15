from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from bson import ObjectId 
# Import load_dotenv function from dotenv module
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file into the running application
def configure():
    load_dotenv()
    
# Get the value of the MONGO_PASSWORD environment variable
configure()

password1 = os.getenv('MONGO_PASSWORD1')

uri1 = f"mongodb+srv://rajsatyam8532:{password1}@cluster0.sq3cdvo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Send a ping to confirm a successful connection
def test_conn(client : MongoClient):
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

def get_client():
    # Create a new client and connect to the server
    client = MongoClient(uri1, server_api=ServerApi('1'))
    return client


####################################
sample_data = {'_id': ObjectId('66253e280c85bcd4e9b63f57'), 'userId': '6620c35e26a6c64a8c4b5870', 'cropId': 'rice181', 'crop': 'Rice', 'startDate': datetime.datetime(1970, 1, 20, 18, 29, 54, 600000), 'lastUpdate': datetime.datetime(1970, 1, 20, 18, 29, 54, 600000), 'location': {'latitude': 23.831457, 'longitude': 91.2867777}, 'area': 6000, 'water': [0], 'harvested': False, '__v': 0}

api = "https://power.larc.nasa.gov/api/temporal/daily/point?start=20240218&end=20240219&latitude=23.831457&longitude=91.286777&community=ag&parameters=T2M&format=json&header=true&time-standard=lst"
##########################




