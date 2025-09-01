from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Basic AI API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello from Dockerized AI API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "basic-ai-api"}

@app.get("/ai/predict")
async def predict():
    # Simple mock AI prediction
    return {
        "prediction": "This is a mock AI prediction",
        "confidence": 0.95,
        "model": "basic-model-v1"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
