Feature: Docker AI Security Experiments Repository
  As a developer and DevOps engineer
  I want to explore various Docker security and AI deployment patterns
  So that I can learn best practices for containerizing AI applications securely

  Background:
    Given the awesome-docker-experiments repository exists
    And all example projects are properly structured
    And each project has appropriate documentation

  Scenario: Repository structure is well-organized
    Given I am exploring the repository
    When I examine the directory structure
    Then I should find examples for basic Dockerfile usage
    And I should find examples for multi-stage builds
    And I should find examples for Docker Compose orchestration
    And I should find examples for GPU-accelerated AI workloads
    And I should find examples for security scanning
    And I should find examples for health checks
    And I should find examples for CI/CD pipeline configuration

  Scenario: Each project can be built independently
    Given I select any example project
    When I navigate to the project directory
    And I build the Docker image
    Then the build should complete successfully
    And the resulting image should be functional
    And the project should work in isolation

  Scenario: Documentation is comprehensive
    Given I am learning about Docker AI security
    When I read the project documentation
    Then each example should have clear instructions
    And the README should explain the purpose and usage
    And best practices should be highlighted
    And security considerations should be documented

  Scenario: Build script automates all examples
    Given the build-all.sh script exists
    When I execute the build script
    Then all Docker examples should be built automatically
    And the script should handle any build dependencies
    And error handling should be robust
    And progress should be clearly indicated

  Scenario: Test coverage is comprehensive
    Given each project has associated tests
    When I run the test suites
    Then unit tests should validate individual components
    And integration tests should validate end-to-end functionality
    And Docker-specific tests should validate containerization
    And feature files should document expected behavior

  Scenario: Security best practices are demonstrated
    Given I am learning about Docker security
    When I examine the security-focused examples
    Then I should see non-root user configurations
    And I should see minimal base image usage
    And I should see vulnerability scanning integration
    And I should see secure secrets management
    And I should see network security configurations

  Scenario: AI workload patterns are covered
    Given I want to containerize AI applications
    When I explore the AI-focused examples
    Then I should find basic API containerization patterns
    And I should find GPU acceleration examples
    And I should find multi-service AI architectures
    And I should find model management strategies

  Scenario: DevOps integration is demonstrated
    Given I want to implement CI/CD for Docker AI applications
    When I examine the pipeline examples
    Then I should find automated testing strategies
    And I should find security scanning integration
    And I should find multi-platform build configurations
    And I should find deployment automation examples

  Scenario: Performance optimization techniques are shown
    Given I want to optimize Docker images for production
    When I study the optimization examples
    Then I should learn about multi-stage builds
    And I should understand layer caching strategies
    And I should see image size reduction techniques
    And I should find runtime performance optimizations

  Scenario: Monitoring and observability are addressed
    Given I want to monitor containerized AI applications
    When I examine the monitoring examples
    Then I should find health check implementations
    And I should see logging configuration examples
    And I should find metrics collection strategies
    And I should understand debugging techniques

  Scenario: Scalability patterns are demonstrated
    Given I want to scale AI applications horizontally
    When I explore the scaling examples
    Then I should find load balancing configurations
    And I should see service orchestration patterns
    And I should understand resource management
    And I should find auto-scaling considerations

  Scenario: Educational value is high
    Given I am learning Docker and AI deployment
    When I work through the examples progressively
    Then each example should build upon previous knowledge
    And complexity should increase gradually
    And real-world scenarios should be addressed
    And common pitfalls should be highlighted

  Scenario: Community contribution is facilitated
    Given I want to contribute to the project
    When I examine the contribution guidelines
    Then the project structure should be easy to extend
    And new examples should follow established patterns
    And testing frameworks should be consistent
    And documentation standards should be clear

  Scenario: Cross-platform compatibility is maintained
    Given the examples should work across environments
    When I test on different platforms
    Then Docker configurations should be platform-agnostic
    And builds should succeed on different architectures
    And functionality should be consistent across platforms
    And platform-specific considerations should be documented
