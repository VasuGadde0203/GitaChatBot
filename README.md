# GitaChatBot
- A conversational AI chatbot that provides insights based on the Bhagavad Gita and answers life-related questions.

## Project Overview
- GitaChatBot is an AI-powered chatbot built using FastAPI, Gemini Model, and Vector Databases.
- It allows users to:
  ✔️ Ask questions about life and philosophy, inspired by the Bhagavad Gita
  ✔️ Register, log in, and manage their accounts
  ✔️ Get responses based on embeddings stored in FAISS and S3
  ✔️ Interact via text, with future support for voice conversations
  ✔️ Expand knowledge from additional training books

## Tech Stack
- **Frontend**
  - HTML, CSS, JavaScript
- **Backend**
  - Python (FastAPI)
  - Gemini AI Model
- **Database & Storage**
  - MongoDB (User Data & Conversations)
  - FAISS (Vector Indexing for Faster Retrieval)
  - Amazon S3 (Storing Embeddings & FAISS Indexes)
- **Authentication**
  - User Login, Registration, Logout system

## Future Enhancements
- Integration of additional training books
- Support for voice-based interactions
- Deployment on Cloud Services

## How to Run Locally
-  **Clone the repository**
  - git clone https://github.com/VasuGadde0203/GitaChatBot.git
  - cd GitaChatBot
- **Install dependencies**
  - pip install -r requirements.txt
- **Run the FastAPI backend**
  - uvicorn main:app --reload
- Open index.html in a browser to access the chatbot

 ## Contributions & Feedback
- Feel free to contribute or suggest improvements! 🚀
- Let me know if you need any modifications! 😊

