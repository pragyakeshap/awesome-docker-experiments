#!/bin/bash

# Integration tests for Docker AI Security Lab
set -e

echo "🧪 Starting integration tests for Docker AI Security Lab"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TEST_RESULTS+=("PASS: $1")
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TEST_RESULTS+=("FAIL: $1")
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to test HTTP endpoint
test_http_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local timeout="${4:-10}"
    
    log_info "Testing $name: $url"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$name responded with $response"
        return 0
    else
        log_failure "$name responded with $response (expected $expected_status)"
        return 1
    fi
}

# Function to test container health
test_container_health() {
    local container_name="$1"
    local max_wait="${2:-60}"
    
    log_info "Testing container health: $container_name"
    
    # Wait for container to be healthy
    local count=0
    while [ $count -lt $max_wait ]; do
        status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        
        if [ "$status" = "healthy" ]; then
            log_success "Container $container_name is healthy"
            return 0
        elif [ "$status" = "unhealthy" ]; then
            log_failure "Container $container_name is unhealthy"
            return 1
        fi
        
        sleep 1
        count=$((count + 1))
    done
    
    log_failure "Container $container_name health check timed out"
    return 1
}

# Function to start container and wait for it to be ready
start_and_test_container() {
    local example_dir="$1"
    local container_name="$2"
    local port="$3"
    local health_endpoint="$4"
    
    log_info "Testing example: $example_dir"
    
    cd "$example_dir"
    
    # Start container
    docker-compose up -d
    
    # Wait for container to start
    sleep 5
    
    # Test container health (if health check is available)
    if docker inspect --format='{{.State.Health}}' "$container_name" 2>/dev/null | grep -q "Status"; then
        test_container_health "$container_name"
    else
        log_warn "No health check configured for $container_name"
    fi
    
    # Test HTTP endpoint
    if [ -n "$health_endpoint" ]; then
        test_http_endpoint "$example_dir health endpoint" "http://localhost:$port$health_endpoint" 200 15
    fi
    
    # Cleanup
    docker-compose down
    cd ..
}

# Function to test security scan
test_security_scan() {
    log_info "Testing security scan functionality"
    
    cd "05-security-scans"
    
    # Build image
    docker build -t security-demo:test .
    
    # Check if image was built successfully
    if docker images | grep -q "security-demo.*test"; then
        log_success "Security demo image built successfully"
    else
        log_failure "Failed to build security demo image"
        cd ..
        return 1
    fi
    
    # Test running the application
    docker run -d --name security-test -p 8080:8080 security-demo:test
    sleep 5
    
    # Test endpoints
    test_http_endpoint "Security API health" "http://localhost:8080/health" 200 10
    
    # Test authentication (should fail without API key)
    if test_http_endpoint "Security API without auth" "http://localhost:8080/security-info" 403 10; then
        log_success "Authentication properly blocks unauthorized access"
    else
        log_failure "Authentication not working properly"
    fi
    
    # Cleanup
    docker stop security-test
    docker rm security-test
    cd ..
}

# Function to test GPU container (without actual GPU)
test_gpu_container() {
    log_info "Testing GPU container build (CPU fallback)"
    
    cd "04-langchain-gpu"
    
    # Build image (will fallback to CPU)
    if docker build -t langchain-gpu:test .; then
        log_success "LangChain GPU image built successfully"
    else
        log_failure "Failed to build LangChain GPU image"
        cd ..
        return 1
    fi
    
    # Test running on CPU
    docker run -d --name langchain-test -p 8000:8000 langchain-gpu:test
    sleep 10
    
    test_http_endpoint "LangChain API health" "http://localhost:8000/health" 200 15
    
    # Cleanup
    docker stop langchain-test
    docker rm langchain-test
    cd ..
}

# Function to generate test report
generate_test_report() {
    log_info "Generating test report..."
    
    cat > test-results.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Docker AI Security Lab Integration Tests" tests="$((TESTS_PASSED + TESTS_FAILED))" failures="$TESTS_FAILED" errors="0" time="$(date +%s)">
EOF

    for result in "${TEST_RESULTS[@]}"; do
        if [[ $result == PASS:* ]]; then
            test_name=$(echo "$result" | sed 's/PASS: //')
            echo "  <testcase name=\"$test_name\" classname=\"integration.test\" />" >> test-results.xml
        else
            test_name=$(echo "$result" | sed 's/FAIL: //')
            echo "  <testcase name=\"$test_name\" classname=\"integration.test\">" >> test-results.xml
            echo "    <failure message=\"Test failed\">$test_name</failure>" >> test-results.xml
            echo "  </testcase>" >> test-results.xml
        fi
    done
    
    echo "</testsuite>" >> test-results.xml
}

# Main test execution
main() {
    log_info "Docker AI Security Lab Integration Tests"
    log_info "========================================"
    
    # Test 1: Basic Dockerfile
    start_and_test_container "01-basic-dockerfile" "basic-dockerfile_app_1" "8000" "/health"
    
    # Test 2: Multi-stage builds
    start_and_test_container "02-multistage-builds" "multistage-builds_app_1" "8000" "/health"
    
    # Test 3: Nginx health check
    start_and_test_container "06-nginx-healthcheck" "nginx-health-demo" "8080" "/health"
    
    # Test 4: Security scan
    test_security_scan
    
    # Test 5: GPU container (CPU fallback)
    test_gpu_container
    
    # Test 6: CrewAI compose (basic build test)
    log_info "Testing CrewAI compose build"
    cd "03-crewai-compose"
    if docker-compose build; then
        log_success "CrewAI compose built successfully"
    else
        log_failure "Failed to build CrewAI compose"
    fi
    cd ..
    
    # Generate test report
    generate_test_report
    
    # Summary
    echo
    log_info "Test Summary:"
    log_info "============="
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_failure "Some tests failed. Please check the logs above."
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test containers..."
    docker-compose -f */docker-compose.yml down 2>/dev/null || true
    docker stop $(docker ps -q) 2>/dev/null || true
    docker rm $(docker ps -aq) 2>/dev/null || true
}

# Trap cleanup on exit
trap cleanup EXIT

# Run tests
main "$@"
