from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import main, security.auth

# from pymongo import MongoClient

app = FastAPI()




# List of allowed origins (your frontend URLs)
origins = [
    'http://127.0.0.1:5500',
    'http://localhost:3000'
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # frontend origins that can call backend
    allow_credentials=True,         # allow cookies/authorization headers
    allow_methods=["*"],            # allow all HTTP methods (GET, POST, PUT, DELETE...)
    allow_headers=["*"],            # allow all headers (e.g., Authorization, Content-Type)
)

app.include_router(main.router, prefix="")
app.include_router(security.auth.router, prefix="/auth", tags=["auth"])