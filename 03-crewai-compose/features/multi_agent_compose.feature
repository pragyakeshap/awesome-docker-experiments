Feature: Multi-Agent Docker Compose Stack
  As a system architect
  I want to orchestrate multiple services using Docker Compose
  So that I can create a scalable multi-agent system with load balancing

  Background:
    Given the Docker Compose configuration exists
    And the multi-agent FastAPI application is ready
    And the nginx load balancer configuration is prepared
    And the Redis service is configured

  Scenario: Docker Compose stack starts successfully
    When I run "docker-compose up" command
    Then all services should start without errors
    And the nginx service should be running on port 80
    And the FastAPI application should be running on port 8000
    And the Redis service should be running on port 6379

  Scenario: Nginx load balancer is accessible
    Given the Docker Compose stack is running
    When I send a GET request to "http://localhost/"
    Then the response status should be 200
    And the response should be proxied through nginx
    And the response should come from the FastAPI application

  Scenario: FastAPI multi-agent endpoints work
    Given the Docker Compose stack is running
    When I send a GET request to "/agents"
    Then the response status should be 200
    And the response should contain a list of available agents
    And each agent should have "name", "role", and "status" fields

  Scenario: Agent creation functionality works
    Given the Docker Compose stack is running
    When I send a POST request to "/agents" with agent data
    Then the response status should be 201
    And the agent should be created successfully
    And the agent should appear in the agents list

  Scenario: Task assignment to agents works
    Given the Docker Compose stack is running
    And at least one agent exists
    When I send a POST request to "/tasks" with task data
    Then the response status should be 201
    And the task should be assigned to an available agent
    And the task status should be tracked

  Scenario: Agent collaboration simulation works
    Given the Docker Compose stack is running
    And multiple agents are available
    When I send a POST request to "/collaborate" with collaboration parameters
    Then the response status should be 200
    And the response should show agent interactions
    And each agent should contribute to the collaboration

  Scenario: Redis integration works
    Given the Docker Compose stack is running
    When agents perform operations that require caching
    Then data should be stored in Redis
    And subsequent requests should retrieve cached data
    And the response time should be improved for cached requests

  Scenario: Health checks work for all services
    Given the Docker Compose stack is running
    When I check the health of each service
    Then nginx should report healthy status
    And the FastAPI application should report healthy status
    And Redis should be accessible and responsive

  Scenario: Load balancing distributes requests
    Given the Docker Compose stack is running with multiple app instances
    When I send multiple requests to the nginx endpoint
    Then requests should be distributed across different app instances
    And the load should be balanced according to nginx configuration

  Scenario: Service discovery works
    Given the Docker Compose stack is running
    When services communicate with each other
    Then they should resolve each other by service names
    And the internal network should allow proper communication
    And external access should only be available through nginx

  Scenario: Environment variables are properly configured
    Given the Docker Compose stack is running
    When I inspect the running containers
    Then all required environment variables should be set
    And Redis connection parameters should be correct
    And the application should use the correct configuration

  Scenario: Data persistence works
    Given the Docker Compose stack is running
    When I store data in Redis
    And I restart the Redis container
    Then the data should persist if volumes are configured
    Or the data should be restored from the application if needed

  Scenario: Graceful shutdown works
    Given the Docker Compose stack is running
    When I run "docker-compose down"
    Then all containers should stop gracefully
    And no orphaned processes should remain
    And all networks should be cleaned up properly
