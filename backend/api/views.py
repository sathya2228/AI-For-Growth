import os
import json
import numpy as np
import threading
from pymongo import MongoClient
from django.http import JsonResponse
from rest_framework.decorators import api_view
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import hashlib
import re
import spacy
from datetime import datetime
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from transformers import logging as hf_logging
from bson import ObjectId


# 🔹 Suppress Hugging Face transformers logs
hf_logging.set_verbosity_error()


os.environ["GOOGLE_API_KEY"] = "AIzaSyC6-Y0KjdZwB9E0-BLWdhUcAaf92sHJYrM"  # Replace with your actual API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# 🔹 Initialize the Gemini Model (for both investment assistance and scheduling)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")
scheduling_model = gemini_model  # Using the same model for scheduling

# 🔹 MongoDB Connection
MONGO_URI = "mongodb+srv://sutgJxLaXWo7gKMR:sutgJxLaXWo7gKMR@cluster0.2ytii.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Change if using MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["Bog_Chatbot"]
collection = db["knowledge_base"]
data_collection = db["Data"]        # Collection to read from




embedding_model = SentenceTransformer('jinaai/jina-embeddings-v2-base-en')
print("Embedding dimension:", embedding_model.get_sentence_embedding_dimension())

data_loaded = threading.Event()

chat_history = []

nlp = spacy.load("en_core_web_sm")

def compute_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

# ✅ Custom serializer to handle ObjectId
def serialize_doc(doc):
    """Converts ObjectId to string for JSON serialization"""
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)  # Convert ObjectId to string
    return doc


# ✅ Load data from MongoDB collection
def load_data_from_mongo():
    knowledge_base, file_data = [], []

    for doc in data_collection.find(): 
        doc = serialize_doc(doc)             # Convert ObjectId to string
        file_name = str(doc.get("_id"))      # Use the document ID as unique identifier
        content = json.dumps(doc)            # Convert document to JSON string

        knowledge_base.append(content)
        file_data.append((file_name, content))

    print(f"✅ Loaded {len(file_data)} documents from MongoDB.")
    return knowledge_base, file_data


# ✅ Store embeddings in MongoDB
def store_embeddings_in_mongo():
    knowledge_base, file_data = load_data_from_mongo()

    for file_name, content in file_data:
        content_hash = compute_hash(content)  # Generate hash

        # Check if the content already exists
        existing_doc = collection.find_one({"file_name": file_name}, {"content_hash": 1})

        if existing_doc and existing_doc.get("content_hash") == content_hash:
            print(f"🔹 Skipping {file_name} (Already exists and unchanged)")
            continue

        # Generate and store embeddings only if new or changed
        embedding = embedding_model.encode(content).tolist()  # Convert NumPy array to list

        try:
            collection.update_one(
                {"file_name": file_name}, 
                {"$set": {"content": content, "embedding": embedding, "content_hash": content_hash}},
                upsert=True
            )
            print(f"✅ Stored/Updated {file_name} in MongoDB")
        except Exception as e:
            print(f"❌ Error storing {file_name} in MongoDB: {e}")

    print("✅ Knowledge base processed successfully!")
    data_loaded.set()

def search_mongo_vector(query, top_k=6):
    # Generate embedding for the query
    query_embedding = embedding_model.encode([query])[0].tolist()  

    print(f"🔹 Query Embedding (First 5 values): {query_embedding[:5]}")
    print(f"🔹 Query Embedding Length: {len(query_embedding)}")

    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "updated_vector",  # Must match MongoDB index
                    "path": "embedding",  # Ensure embedding field exists in DB
                    "queryVector": query_embedding,
                    "numCandidates": max(top_k * 2, 10),
                    "limit": top_k,
                    "similarity": "cosine"
                }
            }
        ]
        
        # Execute the search query
        results = collection.aggregate(pipeline)

        # Extract unique contents while preserving order
        unique_contents = []
        seen_contents = set()

        for doc in results:
            content = doc.get("content", "").strip()
            print(f"✅ Found Match: {content[:50]}...")  # Print first 50 chars for debugging
            if content and content not in seen_contents:
                unique_contents.append(content)
                seen_contents.add(content)

        print(f"🔹 Total Matches Found: {len(unique_contents)}")
        return unique_contents

    except Exception as e:
        print(f"❌ Vector search error: {e}")
        return []


def generate_answer_with_rag(query, closest_knowledge_list, chat_history):
    """
    Generates an AI response using retrieved knowledge and chat history.
    """

    # Combine knowledge into a structured format
    combined_knowledge = "\n\n".join(closest_knowledge_list)

    # Define max character limit for knowledge to avoid exceeding model constraints
    max_knowledge_length = 28000  
    if len(combined_knowledge) > max_knowledge_length:
        combined_knowledge = combined_knowledge[:max_knowledge_length]
        print(f"🔹 Knowledge truncated to {len(combined_knowledge)} characters")

    # Extract chat history (keeping only relevant recent messages)
    max_history_length = 5  # Adjust based on chatbot context
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-max_history_length:]])

    # Construct the refined prompt
    prompt = f"""
    You are a professional AI assistant for **Startup Infinity**, helping users with startup funding and investment queries.
    Your main objectives are to **analyze user intent**, provide **engaging insights**, and foster **meaningful interactions**.

    🔹 **User Type Identification:** Determine if the user is an **entrepreneur** or **investor** and tailor responses accordingly.
    🔹 **Clear & Structured Answers:** Refrain from copying directly from the knowledge base; reframe and summarize.
    🔹 **Conversational Context Awareness:** Maintain continuity in responses.

    **📌 Knowledge Base:**  
    {combined_knowledge}

    **💬 Previous Conversation History:**  
    {history_text}

    **❓ User Query:**  
    {query}

    **✍️ Response Instructions:**  
    - Ensure the answer is well-structured without using bullet points . i need it as short paragraphs like maximun 2 to 3 lines do not exceed 5 lines .  
    - If the query is unrelated to startup investments, respond with:  
      *"I'm sorry, but I can only provide answers about Startup Infinity Platform!"*  
    """

    try:
        # Generate response using Gemini API
        response = gemini_model.generate_content(prompt)
        return response.text.strip() if response and response.text else "⚠️ No response generated."
    
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "⚠️ Sorry, we are experiencing high demand. Please try again later!"

        
@api_view(["POST"])
def chatbot_view(request):
    global chat_history

    data_loaded.wait()
    query = request.data.get("query")

    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    try:
        # Step 1: Store user query in chat history
        chat_history.append({"role": "user", "content": query})

        # ✅ Step 4: Retrieve relevant knowledge if no scheduling intent
        closest_knowledge_list = search_mongo_vector(query)

        # ✅ Step 5: Generate a response using RAG
        answer = generate_answer_with_rag(query, closest_knowledge_list, chat_history[-6:])

        # ✅ Step 6: Store assistant response
        chat_history.append({"role": "assistant", "content": answer})

        # ✅ Step 7: Trim chat history to last 6 messages
        chat_history = chat_history[-6:]

        return JsonResponse({"answer": answer})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# ✅ **7. Load Data on Startup (Runs in Background)**
loading_thread = threading.Thread(target=store_embeddings_in_mongo, daemon=True)
loading_thread.start()
