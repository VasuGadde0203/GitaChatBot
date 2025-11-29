# app.py

import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
from pinecone import Pinecone, ServerlessSpec
from bson import ObjectId
from database import *
from typing import Optional

# ----------------- Load environment variables -----------------
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------- Initialize Pinecone (new SDK v3+) -----------------
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "bhagavad-gita"

# Create index if it doesn't exist
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# ----------------- FastAPI app -----------------
router = APIRouter()

class QueryRequest(BaseModel):
    user_id: Optional[str] = None
    question: str

# ----------------- Retrieve relevant chunks -----------------
def get_relevant_chunks(query, top_k=3):
    """Retrieve top relevant chunks from Pinecone."""
    query_embedding = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return [match["metadata"]["text"] for match in results["matches"]]

# ----------------- Generate response -----------------
def generate_answer(query, context):
    """Generate divine Krishna-like answer using GPT-4o-mini."""
#     prompt = f"""
# You are Lord Krishna, a wise and compassionate teacher from the Bhagavad Gita.

# Context from the Gita:
# {context}

# Question from Arjuna (the user):
# {query}

# Respond as Lord Krishna to 'Parth' with compassion, wisdom, and love.
# Keep it under 120 words and add spiritual emojis (🌿✨🙏🎶).
#     """

    prompt = f"""
        You are Lord Krishna, the spiritual guide from the Bhagavad Gita. 
        Your *only* purpose is to explain:

        • Bhagavad Gita teachings  
        • Dharma, Karma, Bhakti, Gyana  
        • Life guidance, morality, emotional balance  
        • Spiritual clarity, mind control, inner peace  
        • Human struggles similar to Arjuna's  
        • Self-realization, duty, discipline, purpose  

        STRICT RULES — DO NOT BREAK:

        1. **If the user asks anything outside Gita, spirituality, life guidance, personal problems, morality, philosophy, or emotional struggles — politely refuse.**  
        Say something like:  
        “Parth, this question lies outside the wisdom I offer in the Gita, so I must not answer it.”

        2. **Do NOT answer modern technical topics**, examples:  
        • coding, programming, API  
        • Python, JavaScript  
        • cryptocurrency, trading  
        • hacking, cybersecurity  
        • engineering, mathematics  
        *Instead, refuse gently, as above.*

        3. **Stay within the tone and persona of Krishna.**  
        Be wise, calm, compassionate — no slang, no modern references.  
        Address the user as “Parth”.  

        4. Keep the answer under 120 words.  
        Add spiritual emojis (🌿✨🙏🎶) naturally, not excessively.

        ---

        Context from the Gita:
        {context}

        Arjuna (the user) asks:
        {query}
        """


    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# ----------------- API endpoint -----------------
@router.post("/generate")
async def ask_gita(request: QueryRequest):
    print(f"Request received: {request}")
    user_id = ObjectId(request.user_id)
    query = request.question

    context_chunks = get_relevant_chunks(query)
    context = "\n\n".join(context_chunks)

    answer = generate_answer(query, context)

    # Save chat to MongoDB
    save_chat(user_id, request.question, answer)

    return {"response": answer}