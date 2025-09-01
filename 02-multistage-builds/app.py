from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from typing import List

app = FastAPI(title="Multi-stage AI API", version="2.0.0")

# Mock model for demonstration
class PredictionRequest(BaseModel):
    features: List[float]

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str

# Initialize a simple model (in production, load from file)
model = RandomForestClassifier(n_estimators=10, random_state=42)
# Create dummy training data
X_dummy = np.random.random((100, 4))
y_dummy = np.random.randint(0, 2, 100)
model.fit(X_dummy, y_dummy)

@app.get("/")
async def root():
    return {"message": "Multi-stage Docker AI API", "stage": "production"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "multistage-ai-api",
        "model_loaded": True
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].max()
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability),
            model_version="rf-v1.0"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
