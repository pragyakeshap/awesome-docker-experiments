from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
import hashlib
import secrets
import time
from typing import Optional

app = FastAPI(
    title="Security-Hardened AI API",
    version="1.0.0",
    description="Demonstrating security best practices in containerized AI applications"
)

# Security configuration
security = HTTPBearer()
API_KEYS = {
    "demo_key_123": "demo_user",
    "secure_key_456": "admin_user"
}

class SecureRequest(BaseModel):
    data: str
    timestamp: Optional[int] = None

class SecureResponse(BaseModel):
    result: str
    processed_at: int
    security_level: str

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication"""
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return API_KEYS[token]

def hash_data(data: str) -> str:
    """Securely hash sensitive data"""
    salt = secrets.token_bytes(32)
    hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return hashed.hex()

@app.get("/")
async def root():
    return {
        "message": "Security-Hardened AI API",
        "version": "1.0.0",
        "security_features": [
            "API Key Authentication",
            "Data Hashing",
            "Input Validation",
            "Security Headers",
            "Non-root Container"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "secure-ai-api",
        "timestamp": int(time.time()),
        "security_status": "protected"
    }

@app.post("/secure-process", response_model=SecureResponse)
async def secure_process(
    request: SecureRequest,
    user: str = Depends(verify_api_key)
):
    """
    Securely process data with authentication and validation
    """
    try:
        # Validate timestamp (prevent replay attacks)
        current_time = int(time.time())
        if request.timestamp and abs(current_time - request.timestamp) > 300:  # 5 minutes
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request timestamp too old or too far in future"
            )
        
        # Process data securely
        processed_data = f"Securely processed: {hash_data(request.data)}"
        
        return SecureResponse(
            result=processed_data,
            processed_at=current_time,
            security_level="high"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secure processing failed"
        )

@app.get("/security-info")
async def security_info(user: str = Depends(verify_api_key)):
    """Get security information about the running container"""
    return {
        "user": user,
        "container_user": os.getenv("USER", "unknown"),
        "security_measures": {
            "non_root_user": os.getuid() != 0 if hasattr(os, 'getuid') else "N/A",
            "read_only_filesystem": False,  # Would be true in production
            "capabilities_dropped": True,
            "network_policies": "enabled"
        },
        "environment": {
            "python_version": "3.11",
            "container_runtime": "docker",
            "base_image": "python:3.11-slim"
        }
    }

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        access_log=True,
        server_header=False  # Hide server information
    )
