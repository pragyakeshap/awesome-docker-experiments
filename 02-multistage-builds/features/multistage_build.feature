Feature: Multi-stage Docker Build Optimization
  As a DevOps engineer
  I want to use multi-stage Docker builds
  So that I can create smaller, more secure production images

  Background:
    Given the multi-stage Dockerfile exists
    And the FastAPI application source code is available

  Scenario: Multi-stage build creates optimized image
    When I build the Docker image using multi-stage Dockerfile
    Then the build should complete successfully
    And the final image should be smaller than a single-stage equivalent
    And the final image should not contain development dependencies
    And the final image should not contain source code compilation artifacts

  Scenario: Production image functionality is preserved
    Given the multi-stage Docker image is built
    When I run a container from the production image
    Then the FastAPI application should start successfully
    And all API endpoints should be functional

  Scenario: API endpoints work in production image
    Given the container is running from the production image
    When I send a GET request to "/"
    Then the response status should be 200
    And the response should contain "message" field with value "Hello from Optimized Multi-stage Build!"

  Scenario: Health check endpoint works in production
    Given the container is running from the production image
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should contain "status" field with value "healthy"
    And the response should contain "service" field with value "multistage-api"

  Scenario: Optimized prediction endpoint works
    Given the container is running from the production image
    When I send a GET request to "/api/predict"
    Then the response status should be 200
    And the response should contain "prediction" field
    And the response should contain "confidence" field
    And the response should contain "model" field with value "optimized-model-v1"

  Scenario: Build stages are properly separated
    When I examine the multi-stage Dockerfile
    Then there should be a "builder" stage for dependencies
    And there should be a "production" stage for runtime
    And the production stage should copy only necessary files from builder
    And the production stage should use a minimal base image

  Scenario: Image size is optimized
    Given both single-stage and multi-stage images are built
    When I compare the image sizes
    Then the multi-stage image should be significantly smaller
    And the size reduction should be at least 30%

  Scenario: Security is improved in production image
    Given the production image is created
    When I scan the image for vulnerabilities
    Then the image should have fewer attack vectors than development image
    And the image should not contain package managers
    And the image should not contain development tools

  Scenario: Build cache is utilized effectively
    Given I have built the image once
    When I rebuild the image without changes
    Then the build should use cached layers
    And the build time should be significantly reduced

  Scenario: Build works with different base images
    Given I modify the Dockerfile to use different base images
    When I build with alpine-based images
    Then the build should complete successfully
    And the resulting image should be even smaller
    When I build with ubuntu-based images
    Then the build should complete successfully
    And all functionality should be preserved
