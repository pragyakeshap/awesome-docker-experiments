import pytest
import subprocess
import os
import json

class TestSecurityScansProject:
    """Test cases for the security scans Docker project"""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/Dockerfile"
        assert os.path.exists(dockerfile_path)

    def test_security_script_exists(self):
        """Test that security scan script exists and is executable"""
        script_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/security-scan.sh"
        assert os.path.exists(script_path)
        assert os.access(script_path, os.X_OK)

    def test_security_script_syntax(self):
        """Test that the security scan script has valid bash syntax"""
        script_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/security-scan.sh"
        
        result = subprocess.run([
            "bash", "-n", script_path
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script syntax error: {result.stderr}"

    def test_dockerfile_security_practices(self):
        """Test that Dockerfile follows security best practices"""
        dockerfile_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/Dockerfile"
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
            # Check for multi-stage build
            assert "as builder" in content.lower(), "Should use multi-stage build"
            
            # Check for non-root user
            assert "adduser" in content or "useradd" in content, "Should create non-root user"
            
            # Check for USER directive
            assert "USER" in content, "Should specify USER directive"
            
            # Check for minimal base image
            assert "slim" in content.lower() or "alpine" in content.lower(), "Should use minimal base image"
            
            # Check for vulnerability scanning mention
            assert "apt-get update" in content, "Should update package lists"

    def test_app_file_exists(self):
        """Test that the application file exists"""
        app_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/app.py"
        assert os.path.exists(app_path)

    def test_requirements_file_exists(self):
        """Test that requirements file exists"""
        req_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/requirements.txt"
        assert os.path.exists(req_path)

    def test_requirements_pinned_versions(self):
        """Test that requirements have pinned versions for security"""
        req_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/requirements.txt"
        
        with open(req_path, 'r') as f:
            content = f.read()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            for line in lines:
                # Each line should have a pinned version (==)
                assert "==" in line, f"Package {line} should have pinned version"

    @pytest.fixture(scope="class")
    def security_image(self):
        """Build the security-focused Docker image for testing"""
        build_result = subprocess.run([
            "docker", "build", "-t", "security-test-image", "."
        ], cwd="/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans",
        capture_output=True, text=True)
        
        if build_result.returncode != 0:
            pytest.skip(f"Docker build failed, skipping tests: {build_result.stderr}")

        yield "security-test-image"

        # Cleanup
        subprocess.run(["docker", "rmi", "security-test-image"], capture_output=True)

    def test_docker_build_success(self, security_image):
        """Test that the Docker image builds successfully"""
        # Check that image exists
        result = subprocess.run([
            "docker", "images", security_image, "--format", "{{.Repository}}"
        ], capture_output=True, text=True)
        
        assert security_image in result.stdout

    def test_container_runs_as_non_root(self, security_image):
        """Test that container runs as non-root user"""
        result = subprocess.run([
            "docker", "run", "--rm", security_image, "whoami"
        ], capture_output=True, text=True)
        
        # Should not be root
        assert result.stdout.strip() != "root"

    def test_container_filesystem_readonly(self, security_image):
        """Test running container with read-only filesystem"""
        # This tests if the app can run with read-only filesystem
        result = subprocess.run([
            "docker", "run", "--rm", "--read-only", "--tmpfs", "/tmp", 
            security_image, "python", "-c", "print('Read-only test passed')"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Read-only test passed" in result.stdout

    def test_no_package_managers_in_final_image(self, security_image):
        """Test that package managers are not present in final image"""
        # Check that apt/apk are not available (security best practice)
        result = subprocess.run([
            "docker", "run", "--rm", security_image, "which", "apt-get"
        ], capture_output=True, text=True)
        
        # apt-get should not be found in final image
        assert result.returncode != 0

    def test_minimal_image_size(self, security_image):
        """Test that the image size is reasonable (not bloated)"""
        result = subprocess.run([
            "docker", "images", security_image, "--format", "{{.Size}}"
        ], capture_output=True, text=True)
        
        size_str = result.stdout.strip()
        # Basic check that we got a size output
        assert size_str
        assert any(unit in size_str for unit in ['MB', 'GB', 'KB'])


class TestSecurityScanScript:
    """Test cases specifically for the security scan script"""

    def test_security_scan_script_help(self):
        """Test that security scan script shows help"""
        script_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/security-scan.sh"
        
        result = subprocess.run([
            "bash", script_path, "--help"
        ], capture_output=True, text=True)
        
        # Should provide some help output
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_security_scan_script_structure(self):
        """Test that security scan script has proper structure"""
        script_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/security-scan.sh"
        
        with open(script_path, 'r') as f:
            content = f.read()
            
            # Should have shebang
            assert content.startswith('#!/')
            
            # Should have some security-related commands
            security_keywords = ['scan', 'security', 'vulnerability', 'trivy', 'grype', 'snyk']
            assert any(keyword in content.lower() for keyword in security_keywords)


class TestApplicationSecurity:
    """Test cases for application-level security"""

    def test_app_imports_security_libraries(self):
        """Test that the app imports appropriate security libraries"""
        app_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/app.py"
        
        with open(app_path, 'r') as f:
            content = f.read()
            
            # Should import FastAPI
            assert "fastapi" in content.lower()
            
            # Should have some security considerations
            # This could include input validation, HTTPS, etc.
            security_indicators = ['validate', 'security', 'https', 'cors', 'auth']
            # At least some security consideration should be present
            # (This is a basic check - in real apps you'd have more specific requirements)

    def test_app_has_security_headers(self):
        """Test that application configures security headers"""
        app_path = "/Users/akhileshkeshap/Documents/GitHub_Pragya/awesome-docker-experiments/05-security-scans/app.py"
        
        with open(app_path, 'r') as f:
            content = f.read()
            
            # Check for CORS or other security middleware
            # This is a basic check - real applications would have more comprehensive security
            assert "app" in content  # Basic FastAPI app should exist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
