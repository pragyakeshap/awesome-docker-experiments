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

class TestMultistageAPI:
    """Test cases for the multi-stage build FastAPI application"""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Multi-stage Docker AI API"

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "multistage-ai-api"

    def test_predict_endpoint(self):
        """Test the prediction endpoint"""
        response = client.post("/predict", json={"features": [1.0, 2.0, 3.0, 4.0]})
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "model_version" in data
        assert isinstance(data["prediction"], int)
        assert isinstance(data["probability"], float)

    def test_predict_endpoint_invalid_data(self):
        """Test the prediction endpoint with invalid data"""
        response = client.post("/predict", json={"features": []})
        assert response.status_code == 400

    def test_invalid_endpoint(self):
        """Test accessing an invalid endpoint returns 404"""
        response = client.get("/invalid")
        assert response.status_code == 404

    def test_app_configuration(self):
        """Test that the app has correct configuration"""
        assert app.title == "Multi-stage AI API"
        assert app.version == "2.0.0"


class TestMultistageDockerIntegration:
    """Integration tests for multi-stage Docker container"""

    @pytest.fixture(scope="class")
    def docker_container(self):
        """Build and run multi-stage Docker container for testing"""
        # Build the Docker image
        build_result = subprocess.run([
            "docker", "build", "-t", "multistage-ai-api-test", "."
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/02-multistage-builds", 
        capture_output=True, text=True)
        
        if build_result.returncode != 0:
            pytest.fail(f"Docker build failed: {build_result.stderr}")

        # Run the container
        container_id = subprocess.run([
            "docker", "run", "-d", "-p", "8002:8000", "multistage-ai-api-test"
        ], capture_output=True, text=True).stdout.strip()

        # Wait for container to start
        time.sleep(5)

        yield container_id

        # Cleanup: stop and remove container
        subprocess.run(["docker", "stop", container_id], capture_output=True)
        subprocess.run(["docker", "rm", container_id], capture_output=True)
        subprocess.run(["docker", "rmi", "multistage-ai-api-test"], capture_output=True)

    def test_docker_container_health(self, docker_container):
        """Test that the containerized app responds correctly"""
        response = requests.get("http://localhost:8002/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_docker_container_predict(self, docker_container):
        """Test that the containerized prediction works"""
        response = requests.post("http://localhost:8002/predict", 
                               json={"features": [1.0, 2.0, 3.0, 4.0]}, 
                               timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data

    def test_image_size_optimization(self):
        """Test that multi-stage build produces smaller image"""
        # This test would compare image sizes in a real scenario
        # For now, we'll just verify the image was built successfully
        result = subprocess.run([
            "docker", "images", "multistage-ai-api-test", "--format", "{{.Size}}"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert result.stdout.strip()  # Should have some output indicating image exists


class TestPerformance:
    """Performance tests for the multi-stage API"""

    def test_response_time(self):
        """Test that API responses are fast"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return client.post("/predict", json={"features": [1.0, 2.0, 3.0, 4.0]})
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for result in results:
            assert result.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
