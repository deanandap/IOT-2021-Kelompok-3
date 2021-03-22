import base64
from datetime import datetime
from google.cloud import datastore

# Project ID
PROJECT_ID = "iot-2021-tim-03"


def save_temperature(event, context):
    # Process is there is a data field
    if 'data' in event:
        print("Writing data to datastore....")

        # Extract data from event object (a dictionary)
        # To accommodate binary types, Data is encoded in a base 64 format, need to convert it
        temp = base64.b64decode(event['data']).decode('utf-8')

        # Create a client to access the datastore
        client = datastore.Client(project=PROJECT_ID)

        # Create a new key to store a new entity
        newKey = client.key("baca suhu")

        # Create a new entity
        newEntity = datastore.Entity(newKey)

        # Fill in its data
        newEntity.update({
            "created": datetime.now(),
            "suhu": temp,
        })

        # Store it
        client.put(newEntity)

        print("Writing completed...")
    
