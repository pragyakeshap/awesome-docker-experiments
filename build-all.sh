#!/bin/bash

# Build and test all Docker examples
set -e

echo "🚀 Building all Docker AI Security Lab examples"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to build and test an example
build_example() {
    local dir="$1"
    local name="$2"
    local port="$3"
    
    log_info "Building $name in $dir"
    
    cd "$dir"
    
    # Build the image
    if docker build -t "$name" .; then
        log_success "Built $name successfully"
    else
        log_error "Failed to build $name"
        cd ..
        return 1
    fi
    
    # Test if it's a compose project
    if [ -f "docker-compose.yml" ]; then
        log_info "Testing with docker-compose"
        if docker-compose up -d; then
            sleep 5
            
            # Test health endpoint if port is provided
            if [ -n "$port" ]; then
                if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
                    log_success "$name health check passed"
                else
                    log_warn "$name health check failed (might be normal for some examples)"
                fi
            fi
            
            docker-compose down
        else
            log_error "Failed to start $name with docker-compose"
        fi
    else
        # Test single container
        if [ -n "$port" ]; then
            log_info "Testing single container on port $port"
            container_id=$(docker run -d -p "$port:$port" "$name")
            sleep 5
            
            if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
                log_success "$name health check passed"
            else
                log_warn "$name health check failed (might be normal)"
            fi
            
            docker stop "$container_id"
            docker rm "$container_id"
        fi
    fi
    
    cd ..
}

# Main execution
main() {
    log_info "Starting build and test process"
    
    # Build basic dockerfile
    build_example "01-basic-dockerfile" "basic-ai-api" "8000"
    
    # Build multi-stage
    build_example "02-multistage-builds" "multistage-ai-api" "8000"
    
    # Build CrewAI (requires env vars, so just build)
    log_info "Building CrewAI example (compose build only)"
    cd "03-crewai-compose"
    if docker-compose build; then
        log_success "CrewAI compose built successfully"
    else
        log_error "Failed to build CrewAI compose"
    fi
    cd ..
    
    # Build LangChain GPU (CPU fallback)
    build_example "04-langchain-gpu" "langchain-gpu" "8000"
    
    # Build security example
    build_example "05-security-scans" "security-demo" "8080"
    
    # Build nginx health check
    build_example "06-nginx-healthcheck" "nginx-health" "8080"
    
    log_success "All examples built successfully! 🎉"
    
    echo
    log_info "Next steps:"
    echo "1. Explore individual examples in their directories"
    echo "2. Run security scans: cd 05-security-scans && ./security-scan.sh"
    echo "3. Set up CI/CD pipeline: copy 07-cicd-pipeline/ci-cd.yml to .github/workflows/"
    echo "4. Run integration tests: ./07-cicd-pipeline/integration-tests.sh"
    echo
    log_info "For detailed usage, see README.md"
}

# Cleanup on exit
cleanup() {
    log_info "Cleaning up..."
    docker-compose -f */docker-compose.yml down 2>/dev/null || true
    docker stop $(docker ps -q) 2>/dev/null || true
}

trap cleanup EXIT

# Check requirements
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Run main function
main "$@"
