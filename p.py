from fastapi import FastAPI,Path
from json import dumps, load
from typing import Optional

app = FastAPI()
json_file_path = "Room Info.json"
# json_file_path = "Occupant Info.json"

with open(json_file_path, 'r') as file:
    data = load(file)

@app.get("/")
def func():
    return dumps({"project": "fastapi development"})

# @app.get("/room-dets/{id}")
# def room_details(id :str):
#     id = id.upper()
#     return dumps(data.get(id))

@app.get("/occupants/{id}")
def occ_info(id: int = Path(description="occupant details", gt=0)):
    return data["occupants"][id]

@app.get("/list")
def rooms(name: Optional[str] = "op"):
    if name.lower() == "rooms":
        return data
    
    else:
        return {"play": "tennis"}