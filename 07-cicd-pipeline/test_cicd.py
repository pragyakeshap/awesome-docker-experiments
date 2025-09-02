"""
Test suite for CI/CD Pipeline Configuration and Integration Tests.

This module contains comprehensive tests for:
- CI/CD pipeline validation
- GitHub Actions workflow testing
- Integration test script validation
- Security scanning configuration
- Multi-platform build testing
"""

import pytest
import yaml
import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import re


class TestConfig:
    """Test configuration constants."""
    PROJECT_ROOT = Path(__file__).parent.parent
    CICD_DIR = Path(__file__).parent
    CICD_WORKFLOW = CICD_DIR / "ci-cd.yml"
    INTEGRATION_SCRIPT = CICD_DIR / "integration-tests.sh"
    
    EXPECTED_EXAMPLES = [
        '01-basic-dockerfile',
        '02-multistage-builds', 
        '03-crewai-compose',
        '04-langchain-gpu',
        '05-security-scans',
        '06-nginx-healthcheck'
    ]


class TestCICDWorkflow:
    """Test CI/CD workflow configuration."""
    
    def test_workflow_file_exists(self):
        """Test that CI/CD workflow file exists."""
        assert TestConfig.CICD_WORKFLOW.exists(), "CI/CD workflow file should exist"
    
    def test_workflow_yaml_valid(self):
        """Test that CI/CD workflow YAML is valid."""
        try:
            with open(TestConfig.CICD_WORKFLOW, 'r') as f:
                workflow = yaml.safe_load(f)
            assert workflow is not None
            assert isinstance(workflow, dict)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in workflow file: {e}")
    
    def test_workflow_structure(self):
        """Test CI/CD workflow has required structure."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check top-level structure
        assert "name" in workflow
        # YAML parses 'on' as boolean True, so check for True instead
        assert True in workflow or "on" in workflow
        assert "env" in workflow
        assert "jobs" in workflow
        
        # Check workflow name
        assert workflow["name"] == "Docker AI Security CI/CD Pipeline"
        
        # Check triggers (stored under True due to YAML parsing)
        triggers = workflow.get(True) or workflow.get("on")
        assert triggers is not None
        assert "push" in triggers
        assert "pull_request" in triggers
        
        # Check environment variables
        env = workflow["env"]
        assert "REGISTRY" in env
        assert "IMAGE_NAME" in env
        assert env["REGISTRY"] == "ghcr.io"
    
    def test_required_jobs_exist(self):
        """Test that all required jobs are defined."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow["jobs"]
        required_jobs = [
            "security-scan",
            "build-and-test", 
            "image-security-scan",
            "integration-tests",
            "deploy-staging",
            "generate-sbom",
            "push-images"
        ]
        
        for job in required_jobs:
            assert job in jobs, f"Required job '{job}' not found in workflow"
    
    def test_security_scan_job(self):
        """Test security scan job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        security_job = workflow["jobs"]["security-scan"]
        
        assert security_job["runs-on"] == "ubuntu-latest"
        
        steps = security_job["steps"]
        step_names = [step["name"] for step in steps]
        
        assert "Checkout code" in step_names
        assert "Run Trivy vulnerability scanner in repo mode" in step_names
        assert "Upload Trivy scan results to GitHub Security tab" in step_names
        assert "Run Hadolint Dockerfile linter" in step_names
    
    def test_build_and_test_job(self):
        """Test build and test job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        build_job = workflow["jobs"]["build-and-test"]
        
        assert build_job["runs-on"] == "ubuntu-latest"
        assert "needs" in build_job
        assert build_job["needs"] == "security-scan"
        
        # Check strategy matrix
        assert "strategy" in build_job
        matrix = build_job["strategy"]["matrix"]
        assert "example" in matrix
        assert set(matrix["example"]) == set(TestConfig.EXPECTED_EXAMPLES)
    
    def test_image_security_scan_job(self):
        """Test image security scan job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        scan_job = workflow["jobs"]["image-security-scan"]
        
        assert scan_job["runs-on"] == "ubuntu-latest"
        assert "needs" in scan_job
        assert scan_job["needs"] == "build-and-test"
        
        # Check matrix strategy
        matrix = scan_job["strategy"]["matrix"]
        assert set(matrix["example"]) == set(TestConfig.EXPECTED_EXAMPLES)
    
    def test_integration_tests_job(self):
        """Test integration tests job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        integration_job = workflow["jobs"]["integration-tests"]
        
        assert integration_job["runs-on"] == "ubuntu-latest"
        assert "needs" in integration_job
        assert integration_job["needs"] == "build-and-test"
        
        steps = integration_job["steps"]
        step_names = [step["name"] for step in steps]
        
        assert "Checkout code" in step_names
        assert "Download all artifacts" in step_names
        assert "Load Docker images" in step_names
        assert "Run integration tests" in step_names
        assert "Generate test report" in step_names
    
    def test_deploy_staging_job(self):
        """Test staging deployment job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        deploy_job = workflow["jobs"]["deploy-staging"]
        
        assert deploy_job["runs-on"] == "ubuntu-latest"
        assert "if" in deploy_job
        assert deploy_job["if"] == "github.ref == 'refs/heads/main'"
        assert "environment" in deploy_job
        assert deploy_job["environment"] == "staging"
        
        needs = deploy_job["needs"]
        assert "image-security-scan" in needs
        assert "integration-tests" in needs
    
    def test_sbom_generation_job(self):
        """Test SBOM generation job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        sbom_job = workflow["jobs"]["generate-sbom"]
        
        assert sbom_job["runs-on"] == "ubuntu-latest"
        assert "needs" in sbom_job
        assert sbom_job["needs"] == "build-and-test"
        
        steps = sbom_job["steps"]
        step_names = [step["name"] for step in steps]
        
        assert "Install Syft" in step_names
        assert "Generate SBOM for all images" in step_names
        assert "Upload SBOM artifacts" in step_names
    
    def test_push_images_job(self):
        """Test image push job configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        push_job = workflow["jobs"]["push-images"]
        
        assert push_job["runs-on"] == "ubuntu-latest"
        assert "if" in push_job
        assert push_job["if"] == "github.ref == 'refs/heads/main'"
        
        needs = push_job["needs"]
        assert "image-security-scan" in needs
        assert "integration-tests" in needs
        
        # Check matrix strategy
        matrix = push_job["strategy"]["matrix"]
        assert set(matrix["example"]) == set(TestConfig.EXPECTED_EXAMPLES)


class TestIntegrationScript:
    """Test integration test script."""
    
    def test_integration_script_exists(self):
        """Test that integration script exists."""
        assert TestConfig.INTEGRATION_SCRIPT.exists(), "Integration script should exist"
    
    def test_integration_script_executable(self):
        """Test that integration script has execute permissions."""
        script_path = TestConfig.INTEGRATION_SCRIPT
        assert os.access(script_path, os.X_OK), "Integration script should be executable"
    
    def test_integration_script_syntax(self):
        """Test that integration script has valid bash syntax."""
        try:
            result = subprocess.run(
                ["bash", "-n", str(TestConfig.INTEGRATION_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, f"Script syntax error: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Script syntax check timed out")
        except FileNotFoundError:
            pytest.skip("bash not available for syntax checking")
    
    def test_integration_script_content(self):
        """Test integration script contains required functions."""
        with open(TestConfig.INTEGRATION_SCRIPT, 'r') as f:
            content = f.read()
        
        # Check for required functions
        required_functions = [
            "log_info",
            "log_success", 
            "log_failure",
            "log_warn",
            "test_http_endpoint"
        ]
        
        for func in required_functions:
            assert f"{func}()" in content, f"Function '{func}' not found in script"
        
        # Check for required test patterns
        assert "set -e" in content, "Script should have 'set -e' for error handling"
        assert "TESTS_PASSED" in content, "Script should track passed tests"
        assert "TESTS_FAILED" in content, "Script should track failed tests"
    
    def test_integration_script_examples_coverage(self):
        """Test that integration script covers all expected examples."""
        with open(TestConfig.INTEGRATION_SCRIPT, 'r') as f:
            content = f.read()
        
        for example in TestConfig.EXPECTED_EXAMPLES:
            assert example in content, f"Example '{example}' not found in integration script"


class TestDockerfileValidation:
    """Test validation of Dockerfiles across projects."""
    
    def test_all_projects_have_dockerfiles(self):
        """Test that all expected projects have Dockerfiles."""
        for example in TestConfig.EXPECTED_EXAMPLES:
            dockerfile_path = TestConfig.PROJECT_ROOT / example / "Dockerfile"
            assert dockerfile_path.exists(), f"Dockerfile missing for {example}"
    
    def test_dockerfile_syntax(self):
        """Test basic Dockerfile syntax validation."""
        for example in TestConfig.EXPECTED_EXAMPLES:
            dockerfile_path = TestConfig.PROJECT_ROOT / example / "Dockerfile"
            if not dockerfile_path.exists():
                continue
                
            with open(dockerfile_path, 'r') as f:
                content = f.read()
            
            # Basic syntax checks
            assert content.strip(), f"Dockerfile for {example} is empty"
            assert "FROM" in content, f"Dockerfile for {example} missing FROM instruction"
            
            # Check for common security practices
            lines = content.split('\n')
            from_lines = [line for line in lines if line.strip().startswith('FROM')]
            
            for from_line in from_lines:
                # Should not use 'latest' tag in production
                if ':latest' in from_line:
                    # This is a warning, not a failure
                    print(f"Warning: {example} uses 'latest' tag in FROM instruction")


class TestSecurityConfiguration:
    """Test security-related configurations."""
    
    def test_trivy_configuration(self):
        """Test Trivy security scanner configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check repo-level Trivy scan
        security_job = workflow["jobs"]["security-scan"]
        trivy_step = None
        
        for step in security_job["steps"]:
            if "trivy" in step.get("name", "").lower():
                trivy_step = step
                break
        
        assert trivy_step is not None, "Trivy scanning step not found"
        assert trivy_step["uses"] == "aquasecurity/trivy-action@master"
        
        # Check image-level Trivy scan
        image_scan_job = workflow["jobs"]["image-security-scan"]
        image_trivy_step = None
        
        for step in image_scan_job["steps"]:
            if "trivy" in step.get("name", "").lower():
                image_trivy_step = step
                break
        
        assert image_trivy_step is not None, "Image Trivy scanning step not found"
    
    def test_hadolint_configuration(self):
        """Test Hadolint Dockerfile linter configuration."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        security_job = workflow["jobs"]["security-scan"]
        hadolint_step = None
        
        for step in security_job["steps"]:
            if "hadolint" in step.get("name", "").lower():
                hadolint_step = step
                break
        
        assert hadolint_step is not None, "Hadolint step not found"
        assert "hadolint/hadolint-action" in hadolint_step["uses"]


@pytest.mark.integration
class TestFullPipelineValidation:
    """Integration tests for the complete CI/CD pipeline."""
    
    def test_workflow_dependencies(self):
        """Test that job dependencies are correctly configured."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow["jobs"]
        
        # Build should depend on security scan
        assert jobs["build-and-test"]["needs"] == "security-scan"
        
        # Image security scan should depend on build
        assert jobs["image-security-scan"]["needs"] == "build-and-test"
        
        # Integration tests should depend on build
        assert jobs["integration-tests"]["needs"] == "build-and-test"
        
        # Staging deployment should depend on both security and integration
        deploy_needs = jobs["deploy-staging"]["needs"]
        assert "image-security-scan" in deploy_needs
        assert "integration-tests" in deploy_needs
        
        # Image push should have same dependencies as deploy
        push_needs = jobs["push-images"]["needs"]
        assert "image-security-scan" in push_needs
        assert "integration-tests" in push_needs
    
    def test_conditional_jobs(self):
        """Test that conditional jobs have correct conditions."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow["jobs"]
        
        # Deploy and push should only run on main branch
        main_branch_condition = "github.ref == 'refs/heads/main'"
        assert jobs["deploy-staging"]["if"] == main_branch_condition
        assert jobs["push-images"]["if"] == main_branch_condition
    
    def test_artifact_flow(self):
        """Test artifact upload and download flow."""
        with open(TestConfig.CICD_WORKFLOW, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow["jobs"]
        
        # Build job should upload artifacts
        build_steps = jobs["build-and-test"]["steps"]
        upload_step = None
        for step in build_steps:
            if "upload-artifact" in step.get("uses", ""):
                upload_step = step
                break
        
        assert upload_step is not None, "Build job should upload artifacts"
        
        # Integration tests should download artifacts
        integration_steps = jobs["integration-tests"]["steps"]
        download_step = None
        for step in integration_steps:
            if "download-artifact" in step.get("uses", ""):
                download_step = step
                break
        
        assert download_step is not None, "Integration job should download artifacts"


class TestProjectStructureValidation:
    """Test validation of overall project structure."""
    
    def test_all_examples_exist(self):
        """Test that all expected example directories exist."""
        for example in TestConfig.EXPECTED_EXAMPLES:
            example_path = TestConfig.PROJECT_ROOT / example
            assert example_path.exists(), f"Example directory '{example}' not found"
            assert example_path.is_dir(), f"'{example}' should be a directory"
    
    def test_required_files_exist(self):
        """Test that required files exist in each example."""
        required_files = ["Dockerfile"]
        
        for example in TestConfig.EXPECTED_EXAMPLES:
            example_path = TestConfig.PROJECT_ROOT / example
            if not example_path.exists():
                continue
                
            for required_file in required_files:
                file_path = example_path / required_file
                assert file_path.exists(), f"Required file '{required_file}' missing in {example}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
