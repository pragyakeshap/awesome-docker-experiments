Feature: Docker Security Scanning and Hardening
  As a security engineer
  I want to implement comprehensive security scanning for Docker containers
  So that I can identify and mitigate security vulnerabilities

  Background:
    Given the security-focused FastAPI application exists
    And the hardened Dockerfile is configured
    And security scanning tools are available

  Scenario: Secure application endpoints work
    Given the secure container is running
    When I send a GET request to "/"
    Then the response status should be 200
    And the response should contain security headers
    And the response should indicate a secure application

  Scenario: Security health check is functional
    Given the secure container is running
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should contain "status" field with value "healthy"
    And the response should contain "service" field with value "secure-api"
    And security information should be included

  Scenario: Security scan endpoint provides vulnerability info
    Given the secure container is running
    When I send a GET request to "/security/scan"
    Then the response status should be 200
    And the response should contain security scan results
    And the response should include dependency information
    And vulnerability counts should be reported

  Scenario: Security headers are properly configured
    Given the secure container is running
    When I send any request to the application
    Then the response should include security headers
    And "X-Content-Type-Options" should be set to "nosniff"
    And "X-Frame-Options" should be set to "DENY"
    And "X-XSS-Protection" should be configured
    And "Strict-Transport-Security" should be set if HTTPS

  Scenario: Dockerfile security best practices are followed
    Given the security-hardened Dockerfile exists
    When I analyze the Dockerfile structure
    Then it should use a minimal base image
    And it should not run as root user
    And it should use specific version tags, not 'latest'
    And it should minimize the number of layers
    And it should not include unnecessary packages

  Scenario: Container runs with non-root user
    Given the secure container is running
    When I inspect the running container
    Then the application should be running as a non-root user
    And the user should have minimal required permissions
    And sensitive files should not be accessible

  Scenario: Security scanning script executes successfully
    Given the security scan script exists
    When I execute the security scan script
    Then the script should complete without errors
    And vulnerability reports should be generated
    And the reports should be in the expected format

  Scenario: Image vulnerability scanning with Trivy
    Given the Docker image is built
    When I run Trivy security scan on the image
    Then the scan should complete successfully
    And vulnerabilities should be categorized by severity
    And high/critical vulnerabilities should be identified
    And a report should be generated in JSON format

  Scenario: Static code analysis with Bandit
    Given the Python application code exists
    When I run Bandit security analysis
    Then the analysis should complete successfully
    And security issues in code should be identified
    And a report should be generated with severity levels

  Scenario: Dependency vulnerability scanning with Safety
    Given the requirements.txt file exists
    When I run Safety check on dependencies
    Then the check should complete successfully
    And vulnerable dependencies should be identified
    And recommendations for updates should be provided

  Scenario: Container filesystem is secured
    Given the secure container is running
    When I inspect the container filesystem
    Then sensitive files should have proper permissions
    And the filesystem should be read-only where possible
    And temporary directories should be properly secured

  Scenario: Network security is configured
    Given the secure container is running
    When I analyze the network configuration
    Then only necessary ports should be exposed
    And the container should use secure networking
    And internal communications should be encrypted if applicable

  Scenario: Secrets management is implemented
    Given the application requires sensitive configuration
    When the container is deployed
    Then secrets should not be embedded in the image
    And environment variables should be used for sensitive data
    And secrets should be injected at runtime

  Scenario: Runtime security monitoring
    Given the secure container is running
    When I monitor runtime behavior
    Then unusual activities should be detected
    And security events should be logged
    And the container should fail securely on errors

  Scenario: Compliance with security standards
    Given the container is configured for security
    When I validate against security benchmarks
    Then the configuration should meet CIS Docker Benchmark standards
    And OWASP container security guidelines should be followed
    And compliance reports should be generated

  Scenario: Security update process
    Given a security vulnerability is discovered
    When I update the base image or dependencies
    Then the update process should be automated where possible
    And the updated image should be tested for functionality
    And the security posture should be improved
