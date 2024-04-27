import time
import numpy as np
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from pydantic import BaseModel

# ML
import pandas as pd
from sklearn import preprocessing
import matplotlib.pyplot as plt 
plt.rc("font", size=14)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)

# Random forest
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Decision Tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

app = FastAPI()

activity_state = "normal"
state_change_time = time.time()  # Track when the last state change occurred

PATH_TO_TRAINING_DATA = r"combined_dog_data.csv"

# Local Database
#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/smartypaws"

# Docker Database
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@roundhouse.proxy.rlwy.net:32915/smartypaws"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Open a connection to the database
conn = engine.connect()

# Execute a SQL command
all_data = conn.execute(text("SELECT * FROM smart_pet_collar_data"))    

class PetDataInput(BaseModel):
    collar_name: str
    steps: int
    heart_rate: int
    temp: float
    timestamp: datetime
    
# Get All Data
@app.get("/")
def read_root():
    data = []
    for row in all_data:
        data.append(str(row))
    return {"Database": data}

# Get Data by Device Name
@app.get("/device/{device_name}")
def get_device_data(device_name: str):
    result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collar_name = :device_name"), {"device_name": device_name})
    data = []
    for row in result:
        data.append(str(row))
    return {"Device": device_name, "Data": data}

# Get Data by Device Name and latest entry
@app.get("/device/{device_name}/latest")
def get_device_latest_data(device_name: str):
    result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collar_name = :device_name AND timestamp = (SELECT MAX(timestamp) FROM smart_pet_collar_data WHERE collar_name = :device_name)"), {"device_name": device_name})
    data = []
    for row in result:
        data.append(str(row))
    return {"Device": device_name, "Latest Data": data}

@app.get("/devices")
def get_devices():
    result = conn.execute(text("SELECT DISTINCT collar_name FROM smart_pet_collar_data"))
    devices = []
    for row in result:
        devices.append(row[0])
    return {"Devices": devices}


# data stream latest entry every 5 seconds
async def generate_data_stream(device_name: str):
    while True:
        result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collar_name = :device_name AND timestamp = (SELECT MAX(timestamp) FROM smart_pet_collar_data WHERE collar_name = :device_name)"),{"device_name": device_name})
        data = []
        for row in result:
            data.append(str(row))
        #print(data)
        yield f"data: {data}\n".encode()
        time.sleep(5)  # Adjust this value to control the update frequency

@app.get("/data/stream/{device_name}")
async def stream_data(device_name: str):
    return StreamingResponse(generate_data_stream(device_name), media_type="text/event-stream")


# yao ci's ML model, for convenience
@app.get("/ml/log_regression/{collarName}")
async def get_predictions_logistic_regression(collarName: str):
    df = get_data_last_2_days_for_collar_name(collarName)
#    column_names = ['collarName', 'temp', 'hbr', 'timestamp', 'health_status'] assume data columns are ordered like this
#    training_data = pd.read_csv(path, header=None, names=column_names) for when the data has no columns
    #extract relevant features
    model = train_logistic_regression_model(read_training_data(PATH_TO_TRAINING_DATA)) #insert path here
    features = df[['temp', 'hbr']]
    df['predicted_health'] = model.predict(features)
    df['predicted_health_probability'] = model.predict_proba(features)[:, 1]

    prediction_counts = df['predicted_health'].value_counts()
    status = 'healthy'
    if prediction_counts.get(1, 0) > prediction_counts.get(0 ,0): #extremely crude measurement
        status = 'sick'
    
    return status

#random forest
@app.get("/ml/random_forest/{collarName}")
async def get_predictions_random_forest(collarName: str):
    df = get_data_last_2_days_for_collar_name(collarName)
#    column_names = ['collarName', 'temp', 'hbr', 'timestamp', 'health_status'] assume data columns are ordered like this
#    training_data = pd.read_csv(path, header=None, names=column_names) for when the data has no columns
    #extract relevant features
    model = train_random_forest_model(read_training_data(PATH_TO_TRAINING_DATA)) #insert path here
    features = df[['temp', 'hbr', 'steps']]
    df['predicted_health'] = model.predict(features)
    df['predicted_health_probability'] = model.predict_proba(features)[:, 1]

    prediction_counts = df['predicted_health'].value_counts()
    status = 'healthy'
    if prediction_counts.get(1, 0) > prediction_counts.get(0 ,0): #extremely crude measurement
        status = 'sick'
    
    return status

#decision tree
@app.get("/ml/decision_tree/{collarName}")
async def get_predictions_random_forest(collarName: str):
    df = get_data_last_2_days_for_collar_name(collarName)
#    column_names = ['collarName', 'temp', 'hbr', 'timestamp', 'health_status'] assume data columns are ordered like this
#    training_data = pd.read_csv(path, header=None, names=column_names) for when the data has no columns
    #extract relevant features
    model = train_decision_tree_model(read_training_data(PATH_TO_TRAINING_DATA)) #insert path here
    features = df[['temp', 'hbr', 'steps']]
    df['predicted_health'] = model.predict(features)
    df['predicted_health_probability'] = model.predict_proba(features)[:, 1]

    prediction_counts = df['predicted_health'].value_counts()
    status = 'healthy'
    if prediction_counts.get(1, 0) > prediction_counts.get(0 ,0): #extremely crude measurement
        status = 'sick'
    
    return status

def read_training_data(path: str):
    column_names = ['temp', 'hbr', 'steps', 'health_status'] #assume data columns are ordered like this
    training_data = pd.read_csv(path, header=None, names=column_names) #for when the data has no columns
#    training_data = pd.read_csv(path, header=0) #assume data is in csv file with column names
    training_data = training_data.dropna()
    print(training_data.shape)
    print(list(training_data.columns))

    return training_data

# only recent data is important for guessing whether the pet is sick
def get_data_last_2_days_for_collar_name(collarName: str):
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    query = f"""
    SELECT * FROM smart_pet_collar_data
    WHERE collar_name = {collarName} AND timestamp >= '{two_days_ago}'
    """

    df = pd.read_sql_query(query, engine, params={'collarName': collarName, 'two_days_ago': two_days_ago})
    new_column_names = ['collarName', 'temp', 'hbr', 'steps', 'timestamp']
    df.columns = new_column_names #just in case; i dont know what the actual column names in the db are
    
    return df

def train_logistic_regression_model(df):
    # Assuming 'df' is your DataFrame and has been preprocessed correctly
    
    # Separate the features and the target variable
    X = df[['temp', 'hbr', 'steps']]  # include only relevant columns
    y = df['health_status']
    
    # split the data into training and test sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create a logistic regression model
    model = LogisticRegression()
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions on the test set
    predictions = model.predict(X_test)
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    
    print("Accuracy of the model: ", accuracy)
    print("Classification Report:\n", report)
    
    return model    



def train_random_forest_model(df):
    # Features and Labels
    X = df[['temp', 'hbr', 'steps']]  # assuming these are the features
    y = df['health_status']

    # Splitting the dataset into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the rf classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)  # tune these params

    # Train the model
    model.fit(X_train, y_train)

    # Predict on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print("Accuracy:", accuracy)
    print("Classification Report:\n", report)

    return model


def train_decision_tree_model(df):
    # Extract features and labels
    X = df[['temp', 'hbr', 'steps']]
    y = df['health_status']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the decision tree classifier
    tree_model = DecisionTreeClassifier(random_state=42)  # Default settings

    # Train the model
    tree_model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = tree_model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print("Accuracy:", accuracy)
    print("Classification Report:\n", report)

    return tree_model
  
# put new data
@app.put("/pet_data")
def put_pet_data(pet_data: PetDataInput):
    with engine.connect() as conn:
        insert_query = text("""
            INSERT INTO smart_pet_collar_data (collar_name, steps, heart_rate, temp, timestamp)
            VALUES (:collar_name, :steps, :heart_rate, :temp, :timestamp)
        """)
        try:
            conn.execute(insert_query, {
                'collar_name': pet_data.collar_name,
                'steps': pet_data.steps,
                'heart_rate': pet_data.heart_rate,
                'temp': pet_data.temp,
                'timestamp': pet_data.timestamp
            })
            conn.commit()
        except:
            conn.rollback()
            raise
    return {"message": "Data inserted successfully"}
