from fastapi import FastAPI, HTTPException, APIRouter
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import db
import os  

# Initialize the Logger
logger = logging.getLogger("authenticate-logger")
logger.setLevel(logging.INFO)

router = APIRouter()


# MongoDB Connection
users_collection = db["users"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Model
class User(BaseModel):
    name: str
    email: str
    password: str
    

# User Models
class UserLogin(BaseModel):
    email: str
    password: str

# Register API
@router.post("/register")
async def register(user: User):
    # Check if user already exists
    logger.info(f"User: {user}")
    print("In register endpoint")
    if users_collection.find_one({"email": user.email}):
        return {"message": "User already exist", "success": "False"}

    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Store user
    users_collection.insert_one({"username": user.name, "email": user.email, "password": hashed_password})
    
    return {"message": "User registered successfully", "success": "True"}

# Login API
@router.post("/login")
async def login(user: UserLogin):
    logger.info(f"Login attempt: {user.email}")
    print("Login attempt")
    # Check if user exists
    user_data = users_collection.find_one({"email": user.email})
    print(f"User Data: {user_data}")
    if not user_data:
        return {"message": "Invalid email or password!", "success": "False"}

    # Verify the password
    if not pwd_context.verify(user.password, user_data["password"]):
        return {"message": "Invalid email or password!", "success": "False"}

    user_id = str(user_data["_id"])

    return {"message": "Login successful!", "success": "True", "user_name": user_data["username"], "user_id": user_id}