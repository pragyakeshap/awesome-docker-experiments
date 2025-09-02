Feature: CI/CD Pipeline for Docker AI Security Lab
  As a DevOps engineer
  I want to implement a comprehensive CI/CD pipeline
  So that I can automate building, testing, and deploying Docker containers securely

  Background:
    Given the GitHub Actions workflow is configured
    And the integration test script exists
    And all Docker projects are properly structured

  Scenario: Pipeline triggers on code changes
    Given the CI/CD workflow is configured
    When code is pushed to the main branch
    Then the pipeline should trigger automatically
    And all required jobs should be queued for execution

  Scenario: Security scanning job executes successfully
    Given the pipeline is triggered
    When the security-scan job runs
    Then Trivy vulnerability scanner should execute on the repository
    And Hadolint should lint all Dockerfiles
    And security scan results should be uploaded to GitHub Security tab
    And the job should complete without blocking errors

  Scenario: Dockerfile linting catches issues
    Given a Dockerfile with syntax errors exists
    When the Hadolint linter runs
    Then the linting should identify the issues
    And the job should fail with descriptive error messages
    And developers should be notified of the problems

  Scenario: Multi-platform Docker builds work
    Given the build-and-test job is executing
    When Docker images are built for multiple examples
    Then builds should succeed for linux/amd64 platform
    And builds should succeed for linux/arm64 platform
    And build cache should be utilized effectively
    And artifacts should be uploaded for each example

  Scenario: Build matrix covers all projects
    Given the CI/CD pipeline is running
    When the build-and-test job executes
    Then all expected Docker examples should be built
    And each example should have its own build matrix entry
    And builds should run in parallel for efficiency

  Scenario: Image security scanning detects vulnerabilities
    Given Docker images are built successfully
    When the image-security-scan job runs
    Then Trivy should scan each built image for vulnerabilities
    And scan results should be saved as artifacts
    And high-severity vulnerabilities should be flagged
    And the pipeline should continue with scan results available

  Scenario: Integration tests validate functionality
    Given all Docker images are built
    When the integration-tests job runs
    Then all built images should be loaded for testing
    And the integration test script should execute
    And functional tests should validate each application
    And test results should be generated in JUnit format

  Scenario: Integration test script works correctly
    Given the integration test script is executable
    When the script runs in the CI environment
    Then it should test all Docker examples
    And it should validate API endpoints
    And it should check container health
    And it should generate proper test reports

  Scenario: Staging deployment is conditional
    Given the pipeline is running on the main branch
    And security scans and integration tests pass
    When the deploy-staging job executes
    Then deployment to staging should proceed
    And staging environment should be updated
    And deployment status should be tracked

  Scenario: SBOM generation creates software bills of materials
    Given Docker images are successfully built
    When the generate-sbom job runs
    Then Syft should be installed and configured
    And SBOM should be generated for each image
    And both JSON and text formats should be created
    And SBOM artifacts should be uploaded for later use

  Scenario: Container image signing and provenance
    Given images are ready for production deployment
    When the push-images job runs on main branch
    Then images should be signed with cosign
    And SLSA provenance should be generated
    And supply chain security should be ensured
    And signed artifacts should be available

  Scenario: Production image push is protected
    Given the pipeline is running
    When attempting to push images to production registry
    Then the push should only occur on main branch
    And all security and integration tests must pass first
    And images should be tagged appropriately
    And the registry should authenticate successfully

  Scenario: Pipeline handles failures gracefully
    Given a job in the pipeline fails
    When subsequent jobs are evaluated
    Then dependent jobs should be skipped appropriately
    And the pipeline should not continue with failed dependencies
    And failure notifications should be sent
    And artifacts from successful jobs should still be available

  Scenario: Artifact management works correctly
    Given the pipeline generates various artifacts
    When jobs complete execution
    Then build artifacts should be available for download
    And security scan results should be preserved
    And test reports should be accessible
    And artifacts should be retained for the appropriate duration

  Scenario: Cache optimization improves performance
    Given the pipeline has run previously
    When subsequent runs execute
    Then Docker layer cache should be utilized
    And dependency cache should speed up builds
    And build times should be reduced for unchanged components

  Scenario: Pipeline security best practices
    Given the CI/CD pipeline is configured
    When examining security configurations
    Then secrets should be properly managed
    And least privilege access should be enforced
    And audit logs should be maintained
    And compliance requirements should be met

  Scenario: Monitoring and alerting for pipeline health
    Given the pipeline is running regularly
    When monitoring pipeline execution
    Then execution metrics should be tracked
    And failure rates should be monitored
    And performance trends should be analyzed
    And alerts should be configured for anomalies

  Scenario: Documentation and compliance reporting
    Given the pipeline executes successfully
    When generating compliance reports
    Then security scan summaries should be available
    And SBOM documents should provide transparency
    And audit trails should be maintained
    And compliance evidence should be generated automatically
