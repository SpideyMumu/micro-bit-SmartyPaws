import time
import numpy as np
import random
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

app = FastAPI()

activity_state = "normal"
state_change_time = time.time()  # Track when the last state change occurred

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@localhost:3306/smartypaws"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Open a connection to the database
conn = engine.connect()

# Execute a SQL command
all_data = conn.execute(text("SELECT * FROM smart_pet_collar_data"))    
    
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
    result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collarName = :device_name"), {"device_name": device_name})
    data = []
    for row in result:
        data.append(str(row))
    return {"Device": device_name, "Data": data}

# Get Data by Device Name and Date
# @app.get("/device/{device_name}/{date}")
# def get_device_data_by_date(device_name: str, date: str):
#     result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collarName = :device_name AND DATE(timestamp) = :date"), {"device_name": device_name, "date": date})
#     data = []
#     for row in result:
#         data.append(str(row))
#     return {"Device": device_name, "Data": data}

# Get Data by Device Name and latest entry
@app.get("/device/{device_name}/latest")
def get_device_latest_data(device_name: str):
    result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collarName = :device_name AND timestamp = (SELECT MAX(timestamp) FROM smart_pet_collar_data WHERE collarName = :device_name)"), {"device_name": device_name})
    data = []
    for row in result:
        data.append(str(row))
    return {"Device": device_name, "Latest Data": data}


async def generate_data_stream(device_name: str):
    while True:
        result = conn.execute(text("SELECT * FROM smart_pet_collar_data WHERE collarName = :device_name AND timestamp = (SELECT MAX(timestamp) FROM smart_pet_collar_data WHERE collarName = :device_name)"),{"device_name": device_name})
        data = []
        for row in result:
            data.append(str(row))
        print(data)
        yield f"data: {data}\n".encode()
        time.sleep(5)  # Adjust this value to control the update frequency

@app.get("/data/stream/{device_name}")
async def stream_data(device_name: str):
    return StreamingResponse(generate_data_stream(device_name), media_type="text/event-stream")