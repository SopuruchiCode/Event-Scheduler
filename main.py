from db import client
from fastapi import UploadFile, File, APIRouter, Request, Depends, HTTPException
from models import event_model
from datetime import datetime, timezone
from os import path
from bson import ObjectId
from fastapi.responses import JSONResponse
import aiofiles
from security.auth import authenticate, oauth2_scheme
from consts import MEDIA_FOLDER


COVER_PHOTO_FOLDER = path.join(MEDIA_FOLDER,"EVENT_COVER_PHOTOS")
router = APIRouter()


def serialize_doc(doc: dict) -> dict: 
    doc["_id"] = str(doc["_id"])

    if doc.get("creator_id", None):
        doc["creator_id"] = str(doc["creator_id"])         #review this later
    return doc 

def custom_json_serializer(doc: dict) -> dict:
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)                         #reviewed version

        elif isinstance(value, datetime):
            doc[key] = value.isoformat()

    return doc

@router.post("/create_event")
async def create_event(request: Request, cover_photo_file: UploadFile | None = File(None), token = Depends(oauth2_scheme)):    
    try: 
        event_data = event_model(** await request.form())
        event = dict(event_data)
    except Exception as e:
        print("Eheh eheh ", e)
        raise HTTPException(401, "Invalid data")

    #event["creator_id"] = ObjectId(event["creator_id"])    #update this future me, let it fill this automatically using the user that issued the request
    
    user = await authenticate(token)
    event["creator_id"] = user.get("_id")                    #done it here

    db = client["main"]["events"]
    if cover_photo_file.filename:
        ext = cover_photo_file.filename.split(".")[-1]
        filename = datetime.strftime(datetime.now(timezone.utc), "%d-%m-%Y-%H-%M-%S") +"."+ ext 

        chunk_size = 1024 * 1024
        async with aiofiles.open(path.join(COVER_PHOTO_FOLDER, filename), "wb") as file:
            while True:
                content = await cover_photo_file.read(chunk_size)
                if not content:
                    break

                await file.write(content)
        
        event["cover-photo"] = filename
    await db.insert_one(event)
    return {"success": "event created successfully"}

@router.get("/my_events")
async def view_my_events(request: Request, token = Depends(oauth2_scheme)):
    user = await authenticate(token)
    user_id = user.get("_id")
    db = client["main"]["events"]
    cursor = db.find(filter = {"creator_id": user_id})
    events = list(await cursor.to_list())
    data = []
    for event in events:
        print(event)
        data.append(custom_json_serializer(event))

        return JSONResponse(content=data)
    
###############################################################################################################

@router.post("/events-by-creator/{creator_id}")
async def view_events_by_creator(creator_id: str):
    try:
        creator_id = ObjectId(creator_id)
        db = client["main"]["events"]
        cursor = db.find(filter = {"creator_id": creator_id})
        events = list(await cursor.to_list())
        data = []

        for event in events:
            print(event)
            data.append(custom_json_serializer(event))

        return JSONResponse(content=data)
    except Exception as e:
        print(e)
        return JSONResponse({"ERROR": "ERR"})
    

@router.post("/test/{name}")
async def test(name):
    db = client["main"]["events"]
    events = list(await db.find({"name":"one"}).to_list())
    data = []

    for e in events:
        data.append(custom_json_serializer(e))
    return data

