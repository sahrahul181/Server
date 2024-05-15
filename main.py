from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle
from bson import ObjectId
import datetime
import db
from KC import get_KC
from water_req import get_ET0
import joblib

# loading Random Forest Classification Model 
model_path = "model/RF_Recommender.pkl"
with open(model_path, "rb") as file:
    RF_recommender = pickle.load(file)
file.close()

encoder_path = "model/label_encoder.pkl"
with open(encoder_path, "rb") as file:
    label_encoder = pickle.load(file)
file.close()



#############################################
model_path = "model/yield_modelrf.joblib"
with open(model_path, "rb") as file:
    RF_yield = joblib.load(file)
file.close()

encoder_path = "model/area_scaler.pkl"
with open(encoder_path, "rb") as file:
    area_scaler = pickle.load(file)
file.close()

encoder_path = "model/fertilizer_scaler.pkl"
with open(encoder_path, "rb") as file:
    fetilizer_scaler = pickle.load(file)
file.close()

encoder_path = "model/rainfall_scaler.pkl"
with open(encoder_path, "rb") as file:
    rainfall_scaler = pickle.load(file)
file.close()

encoder_path = "model/yield_scaler.pkl"
with open(encoder_path, "rb") as file:
    yield_scaler = pickle.load(file)
file.close()

encoder_path = "model/crop_encoder.pkl"
with open(encoder_path, "rb") as file:
    crop_encoder = pickle.load(file)
file.close()

encoder_path = "model/season_encoder.pkl"
with open(encoder_path, "rb") as file:
    season_encoder = pickle.load(file)
file.close()

encoder_path = "model/state_encoder.pkl"
with open(encoder_path, "rb") as file:
    state_encoder = pickle.load(file)
file.close()


#########################################

# Get Client Conn
client = db.get_client()

# Check DB Connection
db.test_conn(client)

MyDb = client["agricare"]
Crops = MyDb["crops"]


####################################################################################

sample_data = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.87974371,
    "humidity": 82.00274423,
    "pH": 6.502985292000001,
    "rainfall": 202.9355362,
}

new_row_processed = {
    "Crop": "Potato",
    "Season": "Kharif     ",
    "State": "Assam",
    "Area": 28755,
    "Production": 317052,
    "Annual_Rainfall": 1260.8,
    "Fertilizer": 2840994,
}

sample_data = {
    "_id": ObjectId("66253e280c85bcd4e9b63f57"),
    "userId": "6620c35e26a6c64a8c4b5870",
    "cropId": "rice181",
    "crop": "Rice",
    "startDate": datetime.datetime(2024, 2, 18, 18, 29, 54, 600000),
    "lastUpdate": datetime.datetime(2024, 2, 18, 18, 29, 54, 600000),
    "lastIrrigation" : None ,
    "location": {"latitude": 23.831457, "longitude": 91.2867777},
    "area": 6000,
    "water": [0],
    "harvested": False,
    "__v": 0,
    "period": 100,
}


######################################

# creating flask server
app = Flask(__name__)
CORS(app)


# crop yield
@app.route("/api/crop_yield", methods=["POST"])
def crop_yield():
    try:
        new_data = request.get_json()
        new_df = pd.DataFrame(new_data, index=[0])
        # Encode categorical variables
        new_df["crop_encoded"] = crop_encoder.transform(new_df["Crop"])
        new_df["season_encoded"] = season_encoder.transform(new_df["Season"])
        new_df["state_encoded"] = state_encoder.transform(new_df["State"])

        # Scale numerical features
        new_df["Area_scaled"] = area_scaler.transform(new_df[["Area"]])
        new_df["Annual_Rainfall_scaled"] = rainfall_scaler.transform(new_df[["Annual_Rainfall"]])
        new_df["Fertilizer_scaled"] = fetilizer_scaler.transform(new_df[["Fertilizer"]])
        
        # Select features
        features = [
            "crop_encoded",
            "state_encoded",
            "season_encoded",
            "Area_scaled",
            "Annual_Rainfall_scaled",
            "Fertilizer_scaled",
        ]
        # Extract features for prediction
        X_new = new_df.loc[:, features]
        y_predict = RF_yield.predict(X_new)
        response = jsonify({"prediction": str(yield_scaler.inverse_transform(y_predict.reshape(-1,1))[0][0])})
        return response
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# crop recommendation
@app.route("/api/crop_recommender", methods=["POST"])
def crop_recommend():
    try:
        new_data = request.get_json()
        new_df = pd.DataFrame(new_data, index=[0])
        
        # selecting features and target
        features = ['N', 'P','K','temperature', 'humidity', 'ph', 'rainfall']
        
        # Extract features for prediction
        X_new = new_df.loc[:, features]

        # prdicting the crop
        prediction = RF_recommender.predict(X_new)
        
        response = jsonify({"prediction": str(label_encoder.inverse_transform(prediction)[0])})
        """ decode the encoded label """
        return response

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# create a api request for dynamic route '/api/crop_details/${crop_id}'
@app.route("/api/crop_details/<string:crop_id>/update", methods=["GET"])
def crop_details(crop_id):
    
    """ convert crop_id to ObjectId """
    object_id = ObjectId(crop_id)
    
    try:
        """Fetches details of a particular crop."""
        crop = Crops.find_one({"_id": object_id})
        # extract data from crop
        start_date = crop["startDate"]
        flag = "lastIrrigation" in crop
        
        
        location = crop["location"]
        longitude = location["longitude"]
        latitude = location["latitude"]
        # print(last_update)
        
        # get previous day
        now = datetime.datetime.now()
        one_day = datetime.timedelta(days=1)
        prev_day = now - one_day
        # print(prev_day)
        
        diff = 0
        if flag == True:
            last_irrigation = crop["lastIrrigation"]
            diff = (last_irrigation-start_date).days
            start_date = last_irrigation + one_day
    
        
        """ Calculating completion date """
        completion_date = start_date + datetime.timedelta(days=crop["period"])
        
        """ check if harvesting completed or not """
        
        if(crop['harvested']==True):
            data ={"$set" :  {"lastUpdate": completion_date, "water": []}}
            result = Crops.find_one_and_update({"_id": object_id}, data)
            # print(result['lastUpdate'])
            return jsonify({"message" : "true"}),200
        
        elif (now - completion_date).days  >= 0:
            data ={"$set" :  {"lastUpdate": completion_date,"lastIrrigation" : None, "water": [] ,"harvested" : True}}
            result = Crops.find_one_and_update({"_id": object_id}, data)
            # print(result['lastUpdate'])
            return jsonify({"message" : "true"}),200
        
        # """ check last updated date """
        elif (now - start_date).days > 0: 
            """ get KC values """
            kc = get_KC(crop["crop"])
            # print(f"KC : {kc}")
            
            """ get et0 values """
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = prev_day.strftime("%Y-%m-%d")
            et0 = get_ET0(latitude, longitude, start_date, end_date)
            # print(f"et0 : {et0}")
            
            
            """ initialize a eempty list for water """
            water = []
            
            # calculate water requirement
            for i in range(len(et0)):
                water.append(kc[i+diff] * et0[i])
                
            """ update the database with new """
            data ={"$set" :  {"lastUpdate": prev_day, "water": water}}
            
            result = Crops.find_one_and_update({"_id": object_id}, data)
            # print(result['lastUpdate'])
        return jsonify({"message" : "true"}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host = "localhost",port= 5000,debug=True)
