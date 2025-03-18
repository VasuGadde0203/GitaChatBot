from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authenticate import router as auth_router
from app import router as app_router

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/auth")  # Auth routes at /auth
app.include_router(app_router, prefix="/bot")  # Gita bot routes at /bot

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# pip install fastapi uvicorn["standard"] pymongo bson python-dotenv pydantic faiss-cpu numpy sentence_transformers google_generativeai