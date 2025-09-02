import pytest
import requests
import redis
import json
import time
import subprocess
import os
from fastapi.testclient import TestClient

# Import the FastAPI app
from app import app

client = TestClient(app)

class TestCrewAIComposeAPI:
    """Test cases for the CrewAI Compose FastAPI application"""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Simple Multi-Agent System API"
        assert "agents" in data
        assert "redis_connected" in data
        assert len(data["agents"]) == 3
        assert "researcher" in data["agents"]
        assert "writer" in data["agents"]
        assert "analyst" in data["agents"]

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "redis" in data
        assert "agents_available" in data
        assert data["agents_available"] == 3

    def test_create_task_researcher(self):
        """Test creating a task with researcher agent"""
        task_data = {
            "task_description": "Research latest AI trends",
            "task_type": "researcher"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "completed"
        assert "Research Agent" in data["result"]
        assert "Research latest AI trends" in data["result"]

    def test_create_task_writer(self):
        """Test creating a task with writer agent"""
        task_data = {
            "task_description": "Write a blog post about Docker",
            "task_type": "writer"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "completed"
        assert "Writer Agent" in data["result"]

    def test_create_task_analyst(self):
        """Test creating a task with analyst agent"""
        task_data = {
            "task_description": "Analyze system performance",
            "task_type": "analyst"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "completed"
        assert "Data Analyst" in data["result"]

    def test_create_task_default_type(self):
        """Test creating a task with default agent type"""
        task_data = {
            "task_description": "Default task"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "completed"
        assert "Research Agent" in data["result"]  # Should default to researcher

    def test_get_task_status(self):
        """Test retrieving task status"""
        # Create a task first
        task_data = {
            "task_description": "Test task for status check",
            "task_type": "researcher"
        }
        create_response = client.post("/tasks", json=task_data)
        task_id = create_response.json()["task_id"]

        # Get task status
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"

    def test_get_nonexistent_task(self):
        """Test retrieving a non-existent task"""
        response = client.get("/tasks/nonexistent-id")
        assert response.status_code == 404

    def test_invalid_task_data(self):
        """Test creating task with invalid data"""
        response = client.post("/tasks", json={})
        assert response.status_code == 422  # Validation error


class TestComposeStackIntegration:
    """Integration tests for the complete Docker Compose stack"""

    @pytest.fixture(scope="class")
    def compose_stack(self):
        """Start the Docker Compose stack for testing"""
        # Start the compose stack
        result = subprocess.run([
            "docker-compose", "up", "-d"
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/03-crewai-compose",
        capture_output=True, text=True)
        
        if result.returncode != 0:
            pytest.fail(f"Docker Compose up failed: {result.stderr}")

        # Wait for services to be ready
        time.sleep(15)

        # Check if services are healthy
        max_retries = 30
        for _ in range(max_retries):
            try:
                health_response = requests.get("http://localhost:80/health", timeout=5)
                if health_response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        else:
            pytest.fail("Services did not become healthy in time")

        yield

        # Cleanup: stop the compose stack
        subprocess.run([
            "docker-compose", "down"
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/03-crewai-compose",
        capture_output=True)

    def test_nginx_proxy_health(self, compose_stack):
        """Test that Nginx proxy works and health endpoint is accessible"""
        response = requests.get("http://localhost:80/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_direct_api_access(self, compose_stack):
        """Test direct access to FastAPI service"""
        response = requests.get("http://localhost:8000/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_redis_connectivity(self, compose_stack):
        """Test Redis connectivity through the API"""
        response = requests.get("http://localhost:80/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["redis"] == "healthy"

    def test_task_creation_via_nginx(self, compose_stack):
        """Test task creation through Nginx proxy"""
        task_data = {
            "task_description": "Integration test task",
            "task_type": "researcher"
        }
        response = requests.post("http://localhost:80/tasks", json=task_data, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "completed"

    def test_task_retrieval_via_nginx(self, compose_stack):
        """Test task retrieval through Nginx proxy"""
        # Create a task first
        task_data = {
            "task_description": "Test task for retrieval",
            "task_type": "writer"
        }
        create_response = requests.post("http://localhost:80/tasks", json=task_data, timeout=10)
        task_id = create_response.json()["task_id"]

        # Retrieve the task
        response = requests.get(f"http://localhost:80/tasks/{task_id}", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id

    def test_multiple_agents_via_nginx(self, compose_stack):
        """Test all agent types through Nginx proxy"""
        agents = ["researcher", "writer", "analyst"]
        
        for agent in agents:
            task_data = {
                "task_description": f"Test task for {agent}",
                "task_type": agent
            }
            response = requests.post("http://localhost:80/tasks", json=task_data, timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert agent.title() in data["result"] or agent == "analyst" and "Data Analyst" in data["result"]

    def test_service_health_checks(self, compose_stack):
        """Test that all services pass their health checks"""
        # Check compose stack status
        result = subprocess.run([
            "docker-compose", "ps"
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/03-crewai-compose",
        capture_output=True, text=True)
        
        assert result.returncode == 0
        # Should contain running services
        assert "Up" in result.stdout


class TestRedisIntegration:
    """Tests specifically for Redis integration"""

    def test_redis_task_storage(self):
        """Test that tasks are properly stored in Redis"""
        # This would require mocking Redis or using a test Redis instance
        # For now, we test through the API which uses Redis
        task_data = {
            "task_description": "Redis storage test",
            "task_type": "researcher"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        
        task_id = response.json()["task_id"]
        
        # Retrieve the task to verify it was stored
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["task_id"] == task_id


class TestLoadAndStress:
    """Load and stress tests for the application"""

    def test_concurrent_task_creation(self):
        """Test creating multiple tasks concurrently"""
        import concurrent.futures
        
        def create_task(i):
            task_data = {
                "task_description": f"Concurrent task {i}",
                "task_type": "researcher"
            }
            return client.post("/tasks", json=task_data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_task, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All tasks should be created successfully
        for result in results:
            assert result.status_code == 200
            assert "task_id" in result.json()

    def test_rapid_health_checks(self):
        """Test rapid successive health check calls"""
        for _ in range(20):
            response = client.get("/health")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
