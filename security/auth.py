from fastapi import File, HTTPException, Depends, APIRouter, Request, Response, UploadFile
from fastapi.security import OAuth2PasswordBearer
# from typing import Annotated
from pydantic import BaseModel
from db import get_user
from security.passwords import hash_password, verify_password
from db import USER_DATABASE, REFRESH_TOKEN_DATABASE
from models import user_model
from bson import ObjectId
from hashlib import sha256
from datetime import datetime, timezone
from security.jwt import create_access_token, create_refresh_token, decode_token
import aiofiles
from os.path import join
from pathlib import Path
from consts import MEDIA_FOLDER


PROFILE_PHOTO_FOLDER = join(MEDIA_FOLDER,"PROFILE PHOTOS")

router = APIRouter()
class login_schema(BaseModel):
    username: str
    password: str

class access_token_form(BaseModel):
    refresh_token: str

class logout_form(BaseModel):
    refresh_token: str
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def authenticate(token) -> dict | None:           #to get user from access token    still working on it
    try:
        payload = await decode_token(token)
    except Exception:
        raise HTTPException(401, "Access token has exired")
    user_id = payload.get("sub")
    user_model = await USER_DATABASE.find_one(filter={"_id": ObjectId(user_id)})
    return user_model


@router.post("/renew-access-token")
async def get_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token: raise HTTPException(401, "No refresh token")
    hashed_token = sha256(refresh_token.encode()).hexdigest()

    db = REFRESH_TOKEN_DATABASE
    data = await db.find_one(filter={"hashed_token": hashed_token})
    if data is None:
        raise HTTPException(404, detail="Token doesn't exist")   #please change this later, I somehow think it's a security risk. not sure yet

    exp_date = datetime.fromtimestamp(data["exp_date"], tz=timezone.utc)
    if (exp_date) <= (datetime.now(timezone.utc)):
        raise HTTPException(401, detail="Expired Token Error")

    if not data["valid"]:
        raise HTTPException(401, detail="Invalid Token Error")
    
    try:
        jwt_payload = await decode_token(refresh_token)           #want to decode  payload
        user_id = jwt_payload.get("sub")
    except  Exception as e:
        print(e)
        raise HTTPException(401, detail="Invalid Token Error3")
    
    user = await USER_DATABASE.find_one(filter={
        "_id": ObjectId(user_id)
    })
    if (user is None) or (not user["is_active"]):
        raise HTTPException(401, detail="Invalid Token Error2")

    token = await create_access_token(user_id, [])      #not sure of scopes yet
    return {"access_token":token}


@router.post("/login")
async def login(request: Request, response: Response):
    form = await request.form()
    form = login_schema(**form)
    form_data = dict(form)
    user = await get_user(form_data["username"])
    try:
        if user is not None:
            if verify_password(form_data["password"], user["password"]):
                access_token = await create_access_token(
                    user_id=str(user["_id"]),
                    scopes=[]
                )
                refresh_token = await create_refresh_token(
                    user_id=str(user["_id"])
                )
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="none",
                    max_age=86400
                )
                return {"access_token": access_token}
        else:
            raise HTTPException(404, "Invalid Credentials")

    except Exception as e:
        print("error at login", e)
        raise HTTPException(404, "Invalid Credentials")
    
@router.post("/signup")
async def create_user(request: Request, profile_pic: UploadFile | None = File(None)):

    user_data = user_model(** await request.form())
    user = dict(user_data)
    db = USER_DATABASE
    
    if await db.count_documents(filter={"username":user["username"]}):
        raise HTTPException(404, "User already exists")
    
    user["password"] = hash_password(user["password"])
    user["date_created"] = datetime.now(tz=timezone.utc)
    result = await db.insert_one(user)
    _id = result.inserted_id
    _id_str = str(_id)

    if profile_pic.filename:
        ext = profile_pic.filename.split(".")[-1]
        updated_filename = "profile_pic-"+ _id_str + datetime.strftime(datetime.now(tz=timezone.utc), "%d-%m-%Y-%H-%M-%S") +"."+ ext

        chunk_size = 1024 * 1024
        dest_dir = Path(join(PROFILE_PHOTO_FOLDER, f"{_id_str}"))
        if not dest_dir.exists():
            dest_dir.mkdir()

        path = join(PROFILE_PHOTO_FOLDER, f"{_id_str}", updated_filename)
        async with aiofiles.open(path, "wb") as file:
            while True:
                chunk = await profile_pic.read(chunk_size)
                if not chunk:
                    break
                await file.write(chunk)
        await db.find_one_and_update({"_id": _id}, 
                                        {
                                        "$set": {"profile_pic": path}
                                        })
        # user["profile_pic"] = path       
    return {"success": "User successfully created"}

    
@router.post("/logout")
async def logout(logout_form: logout_form):
    refresh_token = logout_form.refresh_token
    hashed_token = sha256(refresh_token.encode()).hexdigest()

    data = await REFRESH_TOKEN_DATABASE.find_one(filter={"hashed_token": hashed_token})
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    # exp_date = datetime.fromtimestamp(data["exp_date"], tz=timezone.utc)           #i think jwt ttl already does this
    # if (exp_date) <= (datetime.now(timezone.utc)):
    #     raise HTTPException(401, detail="Expired Token Error")
    
    await REFRESH_TOKEN_DATABASE.delete_one(filter={"hashed_token": hashed_token})
    return {"detail": "logout successful"}
    

@router.post("/checking-if-logged-in")
async def check_if_logged_in(request: Request, token: str = Depends(oauth2_scheme)):
    print("Thank you Jesus")
    print(request.cookies.get("refresh_token"))
    print(token)