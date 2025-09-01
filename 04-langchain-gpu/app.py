from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
import os
from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

app = FastAPI(title="LangChain GPU-Accelerated API", version="1.0.0")

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Models will be loaded lazily
tokenizer = None
model = None
embeddings = None
vectorstore = None

class ChatRequest(BaseModel):
    message: str
    max_length: int = 100
    temperature: float = 0.7

class DocumentRequest(BaseModel):
    text: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

class QueryRequest(BaseModel):
    query: str
    k: int = 3

def load_model():
    """Load the language model (using a small model for demo)"""
    global tokenizer, model
    if tokenizer is None or model is None:
        model_name = "microsoft/DialoGPT-small"  # Small model for demo
        print(f"Loading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        if device == "cuda":
            model = model.to(device)
        
        # Add padding token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

def load_embeddings():
    """Load embedding model"""
    global embeddings
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': device}
        )

@app.get("/")
async def root():
    return {
        "message": "LangChain GPU-Accelerated API",
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.get("/health")
async def health_check():
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory,
            "gpu_memory_allocated": torch.cuda.memory_allocated(0),
            "gpu_memory_reserved": torch.cuda.memory_reserved(0)
        }
    
    return {
        "status": "healthy",
        "service": "langchain-gpu-api",
        "device": device,
        "gpu_info": gpu_info
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        load_model()
        
        # Encode input
        inputs = tokenizer.encode(request.message, return_tensors="pt")
        if device == "cuda":
            inputs = inputs.to(device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=request.max_length,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "response": response,
            "input_length": len(request.message),
            "output_length": len(response),
            "device_used": device
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/embed-documents")
async def embed_documents(request: DocumentRequest):
    try:
        load_embeddings()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        chunks = text_splitter.split_text(request.text)
        documents = [Document(page_content=chunk) for chunk in chunks]
        
        # Create vector store
        global vectorstore
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="/app/data/chroma_db"
        )
        
        return {
            "status": "success",
            "chunks_created": len(chunks),
            "embedding_model": "all-MiniLM-L6-v2",
            "device_used": device
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document embedding failed: {str(e)}")

@app.post("/query-documents")
async def query_documents(request: QueryRequest):
    try:
        if vectorstore is None:
            raise HTTPException(status_code=400, detail="No documents embedded yet. Use /embed-documents first.")
        
        # Query vector store
        results = vectorstore.similarity_search(request.query, k=request.k)
        
        return {
            "query": request.query,
            "results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results
            ],
            "device_used": device
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document query failed: {str(e)}")

@app.get("/gpu-stats")
async def gpu_stats():
    if not torch.cuda.is_available():
        return {"message": "CUDA not available"}
    
    stats = {}
    for i in range(torch.cuda.device_count()):
        stats[f"gpu_{i}"] = {
            "name": torch.cuda.get_device_name(i),
            "memory_total": torch.cuda.get_device_properties(i).total_memory,
            "memory_allocated": torch.cuda.memory_allocated(i),
            "memory_reserved": torch.cuda.memory_reserved(i),
            "memory_free": torch.cuda.get_device_properties(i).total_memory - torch.cuda.memory_allocated(i)
        }
    
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
