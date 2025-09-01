from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import redis
from typing import Optional
import json
import uuid
import time

app = FastAPI(title="Simple Multi-Agent System", version="1.0.0")

# Redis connection
try:
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    redis_client.ping()  # Test connection
    print("✅ Connected to Redis")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    redis_client = None

class TaskRequest(BaseModel):
    task_description: str
    task_type: str = "research"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None

class Agent:
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
    
    def execute_task(self, task_description: str) -> str:
        # Simulate AI agent work
        time.sleep(1)
        return f"[{self.name}] Completed: {task_description}"

# Initialize simple agents
agents = {
    "researcher": Agent("Research Agent", "Researcher", "Find and analyze information"),
    "writer": Agent("Writer Agent", "Content Creator", "Create engaging content"),
    "analyst": Agent("Data Analyst", "Analyst", "Analyze data and provide insights")
}

@app.get("/")
async def root():
    return {
        "message": "Simple Multi-Agent System API",
        "agents": list(agents.keys()),
        "redis_connected": redis_client is not None
    }

@app.get("/health")
async def health_check():
    redis_status = "connected" if redis_client else "disconnected"
    try:
        if redis_client:
            redis_client.ping()
            redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "agents_available": len(agents)
    }

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest):
    task_id = str(uuid.uuid4())
    
    # Select agent based on task type
    agent_name = task_request.task_type if task_request.task_type in agents else "researcher"
    agent = agents[agent_name]
    
    try:
        # Execute task
        result = agent.execute_task(task_request.task_description)
        
        # Store in Redis if available
        if redis_client:
            task_data = {
                "task_id": task_id,
                "task_description": task_request.task_description,
                "task_type": task_request.task_type,
                "agent": agent_name,
                "result": result,
                "status": "completed",
                "timestamp": time.time()
            }
            redis_client.setex(f"task:{task_id}", 3600, json.dumps(task_data))
        
        return TaskResponse(
            task_id=task_id,
            status="completed",
            result=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        task_data = redis_client.get(f"task:{task_id}")
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        data = json.loads(task_data)
        return TaskResponse(
            task_id=data["task_id"],
            status=data["status"],
            result=data.get("result")
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid task data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")

@app.get("/agents")
async def list_agents():
    return {
        "agents": [
            {
                "name": agent.name,
                "role": agent.role,
                "goal": agent.goal
            }
            for agent in agents.values()
        ]
    }

@app.get("/redis/info")
async def redis_info():
    if not redis_client:
        return {"status": "Redis not connected"}
    
    try:
        info = redis_client.info()
        return {
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "uptime": info.get("uptime_in_seconds")
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
