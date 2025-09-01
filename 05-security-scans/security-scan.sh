#!/bin/bash

# Security scanning script for Docker images
set -e

IMAGE_NAME=${1:-"security-demo:latest"}
REPORT_DIR="./security-reports"

echo "🔒 Starting security scan for image: $IMAGE_NAME"

# Create reports directory
mkdir -p $REPORT_DIR

echo "📋 Step 1: Building image with security best practices..."
docker build -t $IMAGE_NAME .

echo "🔍 Step 2: Running Trivy vulnerability scan..."
# Install trivy if not present
if ! command -v trivy &> /dev/null; then
    echo "Installing Trivy..."
    # For macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install trivy
    # For Linux
    else
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    fi
fi

# Run Trivy scan
trivy image --format json --output $REPORT_DIR/trivy-report.json $IMAGE_NAME
trivy image --format table --output $REPORT_DIR/trivy-report.txt $IMAGE_NAME

echo "🧾 Step 3: Generating SBOM (Software Bill of Materials)..."
# Generate SBOM using Docker's built-in buildx
docker buildx imagetools inspect $IMAGE_NAME --format "{{json .}}" > $REPORT_DIR/image-manifest.json

# Alternative: Use syft for SBOM generation
if command -v syft &> /dev/null; then
    syft $IMAGE_NAME -o json > $REPORT_DIR/sbom.json
    syft $IMAGE_NAME -o table > $REPORT_DIR/sbom.txt
else
    echo "Syft not found. Install with: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin"
fi

echo "🔐 Step 4: Running Docker Scout (if available)..."
if docker scout version &> /dev/null; then
    docker scout cves $IMAGE_NAME --format json --output $REPORT_DIR/scout-report.json
    docker scout cves $IMAGE_NAME --format table --output $REPORT_DIR/scout-report.txt
else
    echo "Docker Scout not available. Install Docker Desktop or CLI plugin."
fi

echo "📊 Step 5: Checking Docker best practices with dive..."
if command -v dive &> /dev/null; then
    dive $IMAGE_NAME --ci --lowestEfficiency=0.95 --highestWastedBytes=20MB > $REPORT_DIR/dive-report.txt 2>&1 || true
else
    echo "Dive not found. Install with: curl -sSfL https://github.com/wagoodman/dive/releases/download/v0.10.0/dive_0.10.0_linux_amd64.tar.gz | tar -xzf - -C /usr/local/bin"
fi

echo "✅ Security scan complete! Reports saved in $REPORT_DIR/"
echo "📁 Generated reports:"
ls -la $REPORT_DIR/

echo "🚨 Critical vulnerabilities found:"
if [ -f "$REPORT_DIR/trivy-report.json" ]; then
    jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | "\(.VulnerabilityID): \(.Title)"' $REPORT_DIR/trivy-report.json | head -5
fi
