
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from database import *
import uuid
from bson import ObjectId
import tempfile
from dotenv import load_dotenv
import boto3

load_dotenv()

router = APIRouter()


AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")    
GOOGLE_API_KEY = os.getenv("GEMINI_API")
genai.configure(api_key=GOOGLE_API_KEY)

# Define request model
class QuestionRequest(BaseModel):
    user_id: str
    question: str
    
    
# Load FAISS index & stored embeddings
# index = faiss.read_index("faiss_hnsw_index.bin")
# with open("embeddings.pkl", "rb") as f:
#     chunks, embeddings = pickle.load(f)

# S3 Bucket Details
S3_BUCKET_NAME = "mongodb-connector-spark"
S3_FAISS_INDEX = "faiss_hnsw_index.bin"
S3_EMBEDDINGS = "embeddings.pkl"

# ✅ Get system's temp directory (Works on Windows, Linux, macOS)
TEMP_DIR = tempfile.gettempdir()
LOCAL_FAISS_INDEX = os.path.join(TEMP_DIR, "faiss_hnsw_index.bin")
LOCAL_EMBEDDINGS = os.path.join(TEMP_DIR, "embeddings.pkl")

# AWS Credentials (Set these in environment variables on Vercel)
AWS_ACCESS_KEY = AWS_ACCESS_KEY
AWS_SECRET_KEY = AWS_SECRET_KEY

# ✅ Function to download files from S3
def download_from_s3(bucket_name, s3_key, local_path):
    s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    
    if not os.path.exists(local_path):  # Download only if not already present
        print(f"Downloading {s3_key} from S3...")
        s3_client.download_file(bucket_name, s3_key, local_path)
        

# ✅ Download FAISS index and embeddings dynamically
download_from_s3(S3_BUCKET_NAME, S3_FAISS_INDEX, LOCAL_FAISS_INDEX)
download_from_s3(S3_BUCKET_NAME, S3_EMBEDDINGS, LOCAL_EMBEDDINGS)

# ✅ Load FAISS index & embeddings
index = faiss.read_index(LOCAL_FAISS_INDEX)
with open(LOCAL_EMBEDDINGS, "rb") as f:
    chunks, embeddings = pickle.load(f)

print("✅ FAISS index and embeddings loaded successfully!")

# Load Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search_gita(query, top_k=3):
    """Search Bhagavad Gita for relevant verses based on a query."""
    
    # Convert query to an embedding
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve top matching text chunks
    return [chunks[i] for i in indices[0]]

def is_greeting(user_input):
    """Check if the user input is a greeting using Gemini."""
    prompt = f"""
        Analyze the following user input and determine if it is a greeting:

        "{user_input}"

        - If it is a greeting, respond with:
        "Yes - Krishna Response: Greet the user in a divine and affectionate way, referring to them as 'My beloved Parth' and using emojis."

        - If it is a casual question directed at Krishna (e.g., 'What are you doing?' or 'Where are you, Krishna?'), respond with:
        "Yes - Krishna Playful Response: Answer playfully as Krishna, with a divine and humorous touch. Example: 'Ah, My dear Parth, I am always here, playing my flute and watching over you. 🌿🎶'"

        If it is NOT a greeting or casual, respond with:
        "No"
    """

    
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    
    response_text = response.text.strip()
    
    if response_text.startswith("Yes"):
        return True, response_text.split("Krishna Response:")[1].strip()
    else:
        return False, ""




def generate_answer(query):
    """Generate a response using GPT-4 based on retrieved verses."""
    
    # Check if input is a greeting
    is_greet, greeting_response = is_greeting(query)
    print(f"Greet: {is_greet}, greeting_response: {greeting_response}")
    
    if is_greet:
        return greeting_response  # Return Krishna's greeting response
    
    # Retrieve relevant verses
    matching_verses = search_gita(query)
    
    # Combine verses into context for GPT-4
    context = "\n".join(matching_verses)
    

    # Create a prompt for GPT-3.5 turbo
    prompt = f"""
    You are a Bhagavad Gita expert. Answer the following question based on these verses:
    
    Context:
    {context}
    
    Question: {query}
    
    Answer in a simple, clear, and helpful way and keep it short under 120 words.
    Address the user as 'Parth' in your response.
    Note: Ensure that in versus, some words may be in some other form, use that words in a english form
    """
    
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    response = model.generate_content(f"{prompt}")
    return response.text


@router.post("/generate")
async def generate_response(request: QuestionRequest):
    print(f"Request: {request}")
    user_id = ObjectId(request.user_id)
    answer = generate_answer(request.question)
    
    save_chat(user_id, request.question, answer)
    return {"response": answer}
