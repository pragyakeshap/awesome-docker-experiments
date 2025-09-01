#!/bin/sh

# Custom health check script for nginx
# This script performs multiple health checks and returns appropriate exit codes

set -e

# Configuration
HEALTH_URL="http://localhost:8080/health"
STATUS_URL="http://localhost:8080/status"
TIMEOUT=5
MAX_RETRIES=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo "${RED}[ERROR]${NC} $1"
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if nginx process is running
check_nginx_process() {
    if pgrep nginx > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    local usage=$(df /tmp | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -lt 90 ]; then
        return 0
    else
        log_warn "Disk usage is high: ${usage}%"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    local mem_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    if [ "$mem_usage" -lt 90 ]; then
        return 0
    else
        log_warn "Memory usage is high: ${mem_usage}%"
        return 1
    fi
}

# Main health check function
perform_health_check() {
    local checks_passed=0
    local total_checks=4

    log_info "Starting health check..."

    # Check 1: Nginx process
    if check_nginx_process; then
        log_info "✓ Nginx process is running"
        checks_passed=$((checks_passed + 1))
    else
        log_error "✗ Nginx process is not running"
    fi

    # Check 2: Health endpoint
    if check_http_endpoint "$HEALTH_URL" 200; then
        log_info "✓ Health endpoint is responding"
        checks_passed=$((checks_passed + 1))
    else
        log_error "✗ Health endpoint is not responding"
    fi

    # Check 3: Status endpoint
    if check_http_endpoint "$STATUS_URL" 200; then
        log_info "✓ Status endpoint is responding"
        checks_passed=$((checks_passed + 1))
    else
        log_error "✗ Status endpoint is not responding"
    fi

    # Check 4: Resource usage
    if check_disk_space && check_memory; then
        log_info "✓ Resource usage is normal"
        checks_passed=$((checks_passed + 1))
    else
        log_warn "✗ Resource usage is concerning"
    fi

    # Determine overall health
    if [ $checks_passed -eq $total_checks ]; then
        log_info "Health check passed: $checks_passed/$total_checks checks successful"
        return 0
    elif [ $checks_passed -ge 2 ]; then
        log_warn "Health check warning: $checks_passed/$total_checks checks successful"
        return 0  # Still consider healthy if critical services work
    else
        log_error "Health check failed: $checks_passed/$total_checks checks successful"
        return 1
    fi
}

# Retry logic
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if perform_health_check; then
        exit 0
    fi
    
    retry_count=$((retry_count + 1))
    if [ $retry_count -lt $MAX_RETRIES ]; then
        log_warn "Health check failed, retrying in 2 seconds... (attempt $retry_count/$MAX_RETRIES)"
        sleep 2
    fi
done

log_error "Health check failed after $MAX_RETRIES attempts"
exit 1
