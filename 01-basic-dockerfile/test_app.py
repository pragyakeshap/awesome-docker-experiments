import pytest
import requests
from fastapi.testclient import TestClient
import json
import time
import subprocess
import os

# Import the FastAPI app
from app import app

client = TestClient(app)

class TestBasicDockerAPI:
    """Test cases for the basic Dockerfile FastAPI application"""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello from Dockerized AI API!"

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "basic-ai-api"

    def test_ai_predict_endpoint(self):
        """Test the AI prediction endpoint"""
        response = client.get("/ai/predict")
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "model" in data
        assert data["confidence"] == 0.95
        assert data["model"] == "basic-model-v1"
        assert isinstance(data["prediction"], str)

    def test_invalid_endpoint(self):
        """Test accessing an invalid endpoint returns 404"""
        response = client.get("/invalid")
        assert response.status_code == 404

    def test_app_title_and_version(self):
        """Test that the app has correct title and version"""
        assert app.title == "Basic AI API"
        assert app.version == "1.0.0"


class TestDockerIntegration:
    """Integration tests for Docker container functionality"""

    @pytest.fixture(scope="class")
    def docker_container(self):
        """Build and run Docker container for testing"""
        # Build the Docker image
        build_result = subprocess.run([
            "docker", "build", "-t", "basic-ai-api-test", "."
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/01-basic-dockerfile", 
        capture_output=True, text=True)
        
        if build_result.returncode != 0:
            pytest.fail(f"Docker build failed: {build_result.stderr}")

        # Run the container
        container_id = subprocess.run([
            "docker", "run", "-d", "-p", "8001:8000", "basic-ai-api-test"
        ], capture_output=True, text=True).stdout.strip()

        # Wait for container to start
        time.sleep(5)

        yield container_id

        # Cleanup: stop and remove container
        subprocess.run(["docker", "stop", container_id], capture_output=True)
        subprocess.run(["docker", "rm", container_id], capture_output=True)
        subprocess.run(["docker", "rmi", "basic-ai-api-test"], capture_output=True)

    def test_docker_container_health(self, docker_container):
        """Test that the containerized app responds correctly"""
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_docker_container_api(self, docker_container):
        """Test that the containerized API works correctly"""
        # Test predict endpoint
        response = requests.get("http://localhost:8001/ai/predict", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data

    def test_docker_container_root(self, docker_container):
        """Test that the containerized root endpoint works"""
        response = requests.get("http://localhost:8001/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
