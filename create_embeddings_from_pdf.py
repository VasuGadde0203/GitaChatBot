# create_embeddings_from_pdf.py

import os
import openai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import PyPDF2
from tqdm import tqdm
import tiktoken

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Pinecone (new SDK)
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

# ----------- Utility Functions -----------

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a PDF."""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_text(text, max_tokens=500):
    """Splits text into smaller chunks for embedding."""
    enc = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = enc.encode(text)
    for i in range(0, len(tokens), max_tokens):
        yield enc.decode(tokens[i:i + max_tokens])

# ----------- Main Function -----------

def embed_pdf_and_store(pdf_path):
    print(f"📘 Extracting text from: {pdf_path}")
    text_data = extract_text_from_pdf(pdf_path)
    chunks = list(chunk_text(text_data))
    print(f"✂️ Total chunks created: {len(chunks)}")

    print("🧠 Creating embeddings and uploading to Pinecone...")
    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i:i + batch_size]
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        vectors = [
            (f"id-{i+j}", emb.embedding, {"text": batch[j]})
            for j, emb in enumerate(response.data)
        ]
        index.upsert(vectors=vectors)

    print("✅ Upload completed successfully!")

if __name__ == "__main__":
    embed_pdf_and_store("data/Bhagavad-gita_As_It_Is.pdf")
