Feature: Basic AI API Docker Container
  As a developer
  I want to containerize a basic AI API
  So that I can deploy it consistently across environments

  Background:
    Given the basic AI API application is containerized
    And the Docker image is built successfully

  Scenario: API responds to health checks
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should contain "status" field with value "healthy"
    And the response should contain "service" field with value "basic-ai-api"

  Scenario: API provides welcome message
    When I send a GET request to "/"
    Then the response status should be 200
    And the response should contain "message" field with value "Hello from Dockerized AI API!"

  Scenario: AI prediction endpoint works
    When I send a GET request to "/ai/predict"
    Then the response status should be 200
    And the response should contain "prediction" field
    And the response should contain "confidence" field with value 0.95
    And the response should contain "model" field with value "basic-model-v1"
    And the prediction should be a non-empty string

  Scenario: Invalid endpoints return 404
    When I send a GET request to "/invalid-endpoint"
    Then the response status should be 404

  Scenario: Container can be built and deployed
    Given the Dockerfile exists in the project directory
    When I build the Docker image with tag "basic-ai-api"
    Then the build should complete successfully
    And the image should be created
    When I run a container from the image on port 8000
    Then the container should start successfully
    And the API should be accessible on the specified port

  Scenario: Container environment is properly configured
    Given the container is running
    When I inspect the container configuration
    Then the container should expose port 8000
    And the working directory should be set correctly
    And the entry point should start the FastAPI application

  Scenario: API handles concurrent requests
    Given the container is running and accessible
    When I send 10 concurrent requests to "/health"
    Then all requests should return status 200
    And all responses should be consistent

  Scenario: Container resource usage is reasonable
    Given the container is running
    When I monitor the container resource usage
    Then the memory usage should be under 512MB
    And the CPU usage should be minimal during idle state
