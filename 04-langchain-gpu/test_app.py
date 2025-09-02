"""
Test suite for LangChain GPU-Accelerated API.

This module contains comprehensive tests for the LangChain GPU API including:
- Health checks and GPU detection
- Chat endpoint functionality
- Document embedding and querying
- GPU statistics monitoring
- Error handling and edge cases
"""

import pytest
import requests
import json
import time
from typing import Dict, Any
import subprocess
import os
import signal
import atexit


class TestConfig:
    """Test configuration constants."""
    BASE_URL = "http://localhost:8000"
    HEALTH_ENDPOINT = f"{BASE_URL}/health"
    CHAT_ENDPOINT = f"{BASE_URL}/chat"
    EMBED_ENDPOINT = f"{BASE_URL}/embed-documents"
    QUERY_ENDPOINT = f"{BASE_URL}/query-documents"
    GPU_STATS_ENDPOINT = f"{BASE_URL}/gpu-stats"
    ROOT_ENDPOINT = f"{BASE_URL}/"
    
    STARTUP_TIMEOUT = 60  # seconds
    REQUEST_TIMEOUT = 30  # seconds


class APITestClient:
    """Helper class for making API requests during tests."""
    
    @staticmethod
    def make_request(method: str, url: str, **kwargs) -> requests.Response:
        """Make an HTTP request with timeout and error handling."""
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=TestConfig.REQUEST_TIMEOUT,
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")
    
    @staticmethod
    def get(url: str, **kwargs) -> requests.Response:
        """Make a GET request."""
        return APITestClient.make_request("GET", url, **kwargs)
    
    @staticmethod
    def post(url: str, **kwargs) -> requests.Response:
        """Make a POST request."""
        return APITestClient.make_request("POST", url, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment and clean up after tests."""
    # Cleanup function
    def cleanup():
        try:
            # Stop any running containers
            subprocess.run(
                ["docker", "stop", "langchain-gpu-test"], 
                capture_output=True, 
                timeout=10
            )
            subprocess.run(
                ["docker", "rm", "langchain-gpu-test"], 
                capture_output=True, 
                timeout=10
            )
        except:
            pass
    
    # Register cleanup to run at exit
    atexit.register(cleanup)
    
    yield
    
    # Cleanup after tests
    cleanup()


class TestHealthEndpoints:
    """Test health check and status endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns basic service information."""
        response = APITestClient.get(TestConfig.ROOT_ENDPOINT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "device" in data
        assert "cuda_available" in data
        assert "gpu_count" in data
        
        assert data["message"] == "LangChain GPU-Accelerated API"
        assert data["device"] in ["cpu", "cuda"]
        assert isinstance(data["cuda_available"], bool)
        assert isinstance(data["gpu_count"], int)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = APITestClient.get(TestConfig.HEALTH_ENDPOINT)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "langchain-gpu-api"
        assert "device" in data
        assert "gpu_info" in data
        
        # If CUDA is available, check GPU info structure
        if data["device"] == "cuda":
            gpu_info = data["gpu_info"]
            assert "gpu_name" in gpu_info
            assert "gpu_memory_total" in gpu_info
            assert "gpu_memory_allocated" in gpu_info
            assert "gpu_memory_reserved" in gpu_info
    
    def test_gpu_stats_endpoint(self):
        """Test GPU statistics endpoint."""
        response = APITestClient.get(TestConfig.GPU_STATS_ENDPOINT)
        
        assert response.status_code == 200
        data = response.json()
        
        # If CUDA is not available, should return appropriate message
        if "message" in data:
            assert data["message"] == "CUDA not available"
        else:
            # If CUDA is available, check stats structure
            for gpu_key, gpu_data in data.items():
                assert gpu_key.startswith("gpu_")
                assert "name" in gpu_data
                assert "memory_total" in gpu_data
                assert "memory_allocated" in gpu_data
                assert "memory_reserved" in gpu_data
                assert "memory_free" in gpu_data


class TestChatEndpoint:
    """Test chat functionality."""
    
    def test_basic_chat(self):
        """Test basic chat functionality."""
        chat_data = {
            "message": "Hello, how are you?",
            "max_length": 50,
            "temperature": 0.7
        }
        
        response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json=chat_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "input_length" in data
        assert "output_length" in data
        assert "device_used" in data
        
        assert data["input_length"] == len(chat_data["message"])
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert data["device_used"] in ["cpu", "cuda"]
    
    def test_chat_with_different_parameters(self):
        """Test chat with different parameter values."""
        test_cases = [
            {"message": "Hi", "max_length": 20, "temperature": 0.1},
            {"message": "Tell me a story", "max_length": 100, "temperature": 0.9},
            {"message": "What is AI?", "max_length": 80, "temperature": 0.5}
        ]
        
        for chat_data in test_cases:
            response = APITestClient.post(
                TestConfig.CHAT_ENDPOINT,
                json=chat_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["input_length"] == len(chat_data["message"])
    
    def test_chat_invalid_input(self):
        """Test chat endpoint with invalid input."""
        # Test missing required field
        response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json={"max_length": 50}
        )
        assert response.status_code == 422
        
        # Test invalid parameter types
        response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json={
                "message": "Hello",
                "max_length": "invalid",
                "temperature": "invalid"
            }
        )
        assert response.status_code == 422
    
    def test_empty_message_chat(self):
        """Test chat with empty message."""
        response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json={"message": ""}
        )
        
        # Should either succeed with empty response or handle gracefully
        assert response.status_code in [200, 400]


class TestDocumentEmbedding:
    """Test document embedding and querying functionality."""
    
    def test_embed_documents(self):
        """Test document embedding functionality."""
        document_data = {
            "text": "This is a test document. It contains multiple sentences. We will split it into chunks for testing the embedding functionality. Each chunk will be processed separately.",
            "chunk_size": 50,
            "chunk_overlap": 10
        }
        
        response = APITestClient.post(
            TestConfig.EMBED_ENDPOINT,
            json=document_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "chunks_created" in data
        assert "embedding_model" in data
        assert "device_used" in data
        
        assert data["chunks_created"] > 0
        assert data["embedding_model"] == "all-MiniLM-L6-v2"
        assert data["device_used"] in ["cpu", "cuda"]
    
    def test_query_documents(self):
        """Test document querying after embedding."""
        # First, embed some documents
        document_data = {
            "text": "Machine learning is a subset of artificial intelligence. Deep learning uses neural networks. Natural language processing deals with text and speech.",
            "chunk_size": 100,
            "chunk_overlap": 20
        }
        
        embed_response = APITestClient.post(
            TestConfig.EMBED_ENDPOINT,
            json=document_data
        )
        assert embed_response.status_code == 200
        
        # Now query the documents
        query_data = {
            "query": "What is machine learning?",
            "k": 2
        }
        
        response = APITestClient.post(
            TestConfig.QUERY_ENDPOINT,
            json=query_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "results" in data
        assert "device_used" in data
        
        assert data["query"] == query_data["query"]
        assert len(data["results"]) <= query_data["k"]
        
        for result in data["results"]:
            assert "content" in result
            assert "metadata" in result
    
    def test_query_without_embedding(self):
        """Test querying without embedding documents first."""
        query_data = {
            "query": "This should fail",
            "k": 1
        }
        
        response = APITestClient.post(
            TestConfig.QUERY_ENDPOINT,
            json=query_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "No documents embedded yet" in data["detail"]
    
    def test_embed_documents_different_params(self):
        """Test embedding with different chunk parameters."""
        test_cases = [
            {"chunk_size": 200, "chunk_overlap": 50},
            {"chunk_size": 100, "chunk_overlap": 0},
            {"chunk_size": 500, "chunk_overlap": 100}
        ]
        
        base_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20
        
        for params in test_cases:
            document_data = {
                "text": base_text,
                **params
            }
            
            response = APITestClient.post(
                TestConfig.EMBED_ENDPOINT,
                json=document_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["chunks_created"] > 0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_endpoints(self):
        """Test invalid endpoint handling."""
        invalid_endpoints = [
            f"{TestConfig.BASE_URL}/invalid",
            f"{TestConfig.BASE_URL}/chat/invalid",
            f"{TestConfig.BASE_URL}/embed/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = APITestClient.get(endpoint)
            assert response.status_code == 404
    
    def test_malformed_json(self):
        """Test handling of malformed JSON requests."""
        response = requests.post(
            TestConfig.CHAT_ENDPOINT,
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=TestConfig.REQUEST_TIMEOUT
        )
        assert response.status_code == 422
    
    def test_large_input_handling(self):
        """Test handling of large inputs."""
        large_message = "A" * 10000  # Very long message
        
        chat_data = {
            "message": large_message,
            "max_length": 100
        }
        
        response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json=chat_data
        )
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 500]


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test a complete workflow from health check to document Q&A."""
        # 1. Check service health
        health_response = APITestClient.get(TestConfig.HEALTH_ENDPOINT)
        assert health_response.status_code == 200
        
        # 2. Test basic chat
        chat_response = APITestClient.post(
            TestConfig.CHAT_ENDPOINT,
            json={"message": "Hello"}
        )
        assert chat_response.status_code == 200
        
        # 3. Embed documents
        embed_response = APITestClient.post(
            TestConfig.EMBED_ENDPOINT,
            json={
                "text": "AI and machine learning are transforming technology. Deep learning enables advanced pattern recognition.",
                "chunk_size": 100,
                "chunk_overlap": 20
            }
        )
        assert embed_response.status_code == 200
        
        # 4. Query documents
        query_response = APITestClient.post(
            TestConfig.QUERY_ENDPOINT,
            json={"query": "What is AI?", "k": 2}
        )
        assert query_response.status_code == 200
        
        # 5. Check GPU stats
        gpu_response = APITestClient.get(TestConfig.GPU_STATS_ENDPOINT)
        assert gpu_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
