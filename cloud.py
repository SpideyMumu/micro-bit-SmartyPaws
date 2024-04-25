import time
import numpy as np
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from pydantic import BaseModel

app = FastAPI()

activity_state = "normal"
state_change_time = time.time()  # Track when the last state change occurred

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

# put new data
@app.put("/pet_data")
def put_pet_data(pet_data: PetDataInput):
    with engine.connect() as conn:
        insert_query = text("""
            INSERT INTO smart_pet_collar_data (collar_name, steps, heart_rate, temp, timestamp)
            VALUES (:collar_name, :steps, :heart_rate, :temp, :timestamp)
        """)
        conn.execute(insert_query, {
            'collar_name': pet_data.collar_name,
            'steps': pet_data.steps,
            'heart_rate': pet_data.heart_rate,
            'temp': pet_data.temp,
            'timestamp': pet_data.timestamp
        })
        conn.commit()
    return {"message": "Data inserted successfully"}