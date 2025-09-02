Feature: Nginx Health Check and Load Balancing
  As a DevOps engineer
  I want to implement comprehensive health checks for nginx
  So that I can ensure reliable load balancing and service availability

  Background:
    Given the nginx Docker configuration exists
    And the health check scripts are configured
    And the Docker Compose setup includes nginx and backend services

  Scenario: Nginx container starts successfully
    Given the nginx Dockerfile is properly configured
    When I build the nginx Docker image
    Then the build should complete successfully
    And the image should contain nginx with custom configuration
    And health check scripts should be included in the image

  Scenario: Basic nginx health check works
    Given the nginx container is running
    When the Docker health check is executed
    Then the health check should return success
    And nginx should be responding to requests
    And the health check endpoint should be accessible

  Scenario: Custom health endpoint is accessible
    Given the nginx container is running
    When I send a GET request to "/health.html"
    Then the response status should be 200
    And the response should contain health status information
    And the response should be served by nginx directly

  Scenario: Health check script validates nginx status
    Given the nginx container is running
    When the health-check.sh script is executed
    Then the script should return exit code 0 for healthy status
    And the script should validate nginx process is running
    And the script should check if nginx is accepting connections

  Scenario: Docker Compose health checks work
    Given the Docker Compose stack is configured with health checks
    When I start the stack with "docker-compose up"
    Then all services should report healthy status
    And nginx should pass its health check
    And dependent services should wait for nginx to be healthy

  Scenario: Nginx configuration is valid
    Given the nginx.conf file exists
    When I validate the nginx configuration
    Then the configuration should be syntactically correct
    And all required directives should be present
    And upstream servers should be properly configured

  Scenario: Load balancing configuration works
    Given nginx is configured with multiple upstream servers
    And the Docker Compose stack includes multiple backend instances
    When I send multiple requests through nginx
    Then requests should be distributed across backend servers
    And the load balancing algorithm should work as expected

  Scenario: Health check detects unhealthy backends
    Given nginx is running with multiple backend servers
    When one of the backend servers becomes unhealthy
    Then nginx should detect the unhealthy backend
    And requests should be routed only to healthy backends
    And the unhealthy backend should be automatically excluded

  Scenario: Health check script handles edge cases
    Given the health check script is configured
    When nginx is temporarily unresponsive
    Then the health check should fail appropriately
    And the script should provide meaningful error messages
    And the container should be marked as unhealthy

  Scenario: Recovery after health check failure
    Given nginx was previously unhealthy
    When the underlying issue is resolved
    Then the health check should start passing again
    And the container should be marked as healthy
    And traffic should resume flowing through nginx

  Scenario: Health check endpoint serves static content
    Given nginx is configured to serve health.html
    When I request the health endpoint
    Then the response should be served from the static file
    And the response should be fast and efficient
    And no backend processing should be required

  Scenario: Docker health check integration
    Given the Dockerfile includes HEALTHCHECK instruction
    When the container is running
    Then Docker should periodically execute the health check
    And the container status should reflect health check results
    And unhealthy containers should be detectable via Docker API

  Scenario: Health check logging and monitoring
    Given nginx is running with health checks enabled
    When health checks are performed
    Then health check results should be logged
    And monitoring systems should be able to access health status
    And historical health data should be available

  Scenario: Performance impact of health checks
    Given health checks are running continuously
    When I monitor nginx performance
    Then health checks should have minimal performance impact
    And the frequency should be appropriate for the use case
    And resource usage should remain reasonable

  Scenario: Health check works with SSL/TLS
    Given nginx is configured with SSL/TLS
    When health checks are performed over HTTPS
    Then the health check should validate SSL certificate
    And secure connections should be properly handled
    And health status should be accurate for HTTPS endpoints

  Scenario: Custom health check parameters
    Given the health check script accepts parameters
    When I customize health check thresholds
    Then the script should respect custom timeout values
    And custom retry counts should be honored
    And different health criteria should be configurable

  Scenario: Integration with orchestration platforms
    Given nginx is deployed in a container orchestration platform
    When the platform performs health checks
    Then the health check should integrate with platform APIs
    And the platform should respect health check results
    And automatic recovery actions should be triggered when appropriate
