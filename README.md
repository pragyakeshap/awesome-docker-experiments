# 🐳 Awesome Docker Experiments

A comprehensive collection of Docker examples demonstrating best practices for AI/ML workloads, security, and cloud-native applications.

## 🎯 Overview

This repository provides hands-on Docker experiments that explore:

### 🤖 AI/ML Containerization
- **CrewAI Multi-Agent Systems** - Orchestrating AI agents with Docker Compose
- **LangChain with GPU Support** - Running LLMs in containers with CUDA acceleration
- **Scalable AI APIs** - FastAPI-based services with proper health checks

### 🔒 Security Best Practices
- **Multi-stage Dockerfiles** - Reducing attack surface and image size
- **Vulnerability Scanning** - Automated security scans with Trivy and SBOM generation
- **Non-root Containers** - Security-hardened container configurations
- **Secret Management** - Secure handling of API keys and credentials

### ☁️ Cloud-Native Patterns
- **Health Checks** - Load balancer and Kubernetes-friendly endpoints
- **CI/CD Pipelines** - Automated testing, security scanning, and deployment
- **Container Orchestration** - Docker Compose stacks with service dependencies
- **Monitoring & Observability** - Basic metrics and logging patterns

---

## 📂 Project Structure

```
awesome-docker-experiments/
├── 01-basic-dockerfile/          # Simple Python API container
├── 02-multistage-builds/         # Security-optimized multi-stage build
├── 03-crewai-compose/            # CrewAI multi-agent system with Redis
├── 04-langchain-gpu/             # LangChain with CUDA GPU support
├── 05-security-scans/            # Vulnerability scanning and SBOM generation
├── 06-nginx-healthcheck/         # Advanced health check patterns
├── 07-cicd-pipeline/             # GitHub Actions CI/CD workflow
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Git

### Clone and Explore

```bash
git clone https://github.com/pragyakeshap/awesome-docker-experiments.git
cd awesome-docker-experiments
```

### Run any example:
```bash
cd 01-basic-dockerfile
docker build -t basic-ai-api .
docker run -p 8000:8000 basic-ai-api
```

### Run All Examples
```bash
# Test all examples with integration script
chmod +x 07-cicd-pipeline/integration-tests.sh
./07-cicd-pipeline/integration-tests.sh
```

---

## 📚 Detailed Examples

### 1. 🐍 Basic Dockerfile (`01-basic-dockerfile/`)

A minimal Python FastAPI application demonstrating fundamental Docker concepts.

**Features:**
- FastAPI web framework
- Non-root user for security
- Health check endpoint
- Proper dependency caching

**Usage:**
```bash
cd 01-basic-dockerfile
docker build -t basic-ai-api .
docker run -p 8000:8000 basic-ai-api

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ai/predict
```

### 2. 🏗️ Multi-stage Builds (`02-multistage-builds/`)

Advanced Dockerfile with multi-stage builds for optimized production images.

**Features:**
- Separate build and runtime stages
- Reduced image size and attack surface
- Build dependency isolation
- Integrated health checks

**Usage:**
```bash
cd 02-multistage-builds
docker build -t multistage-ai-api .
docker run -p 8000:8000 multistage-ai-api

# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.0, 2.0, 3.0, 4.0]}'
```

### 3. 🤖 CrewAI Multi-Agent System (`03-crewai-compose/`)

Complete multi-agent AI system using CrewAI, Redis, and Nginx load balancer.

**Features:**
- Multiple AI agents (Research, Writer, Analyst)
- Redis for task storage
- Nginx reverse proxy
- Docker Compose orchestration
- Environment variable configuration

**Setup:**
```bash
cd 03-crewai-compose

# Copy environment template
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start the stack
docker-compose up -d

# Test the system
curl -X POST http://localhost/execute-task \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Research the latest trends in AI", "task_type": "research"}'
```

### 4. 🚀 LangChain with GPU (`04-langchain-gpu/`)

LangChain application with CUDA GPU support for local LLM inference.

**Features:**
- NVIDIA CUDA base image
- GPU-accelerated transformers
- HuggingFace integration
- Vector database with ChromaDB
- CPU fallback support

**Usage:**
```bash
cd 04-langchain-gpu

# For GPU support (requires NVIDIA Docker runtime)
docker-compose up -d

# For CPU-only testing
docker build -t langchain-gpu .
docker run -p 8000:8000 langchain-gpu

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "max_length": 100}'

# Test document embedding
curl -X POST http://localhost:8000/embed-documents \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a sample document for embedding."}'
```

### 5. 🔒 Security Scanning (`05-security-scans/`)

Comprehensive security scanning setup with vulnerability detection and SBOM generation.

**Features:**
- Trivy vulnerability scanning
- SBOM (Software Bill of Materials) generation
- Docker best practices validation
- Security-hardened Dockerfile
- Automated security reporting

**Usage:**
```bash
cd 05-security-scans

# Build security-hardened image
docker build -t security-demo .

# Run security scan
./security-scan.sh security-demo

# View reports
ls -la security-reports/

# Test secure API
docker run -p 8080:8080 security-demo
curl -H "Authorization: Bearer demo_key_123" \
  http://localhost:8080/security-info
```

### 6. 🏥 Nginx Health Checks (`06-nginx-healthcheck/`)

Advanced health check patterns for load balancers and Kubernetes.

**Features:**
- Multiple health check endpoints (`/health`, `/ready`, `/live`)
- Custom health check script with retry logic
- Load balancer integration with Traefik
- Detailed health status page
- Resource monitoring

**Usage:**
```bash
cd 06-nginx-healthcheck

# Start nginx with health checks
docker-compose up -d

# Test different health endpoints
curl http://localhost:8080/health          # Simple health check
curl http://localhost:8080/ready           # Readiness probe
curl http://localhost:8080/live            # Liveness probe
curl http://localhost:8080/status          # JSON status
curl http://localhost:8080/metrics         # Basic metrics

# View detailed health page
open http://localhost:8080/health/detailed

# Start with load balancer (optional)
docker-compose --profile loadbalancer up -d
open http://localhost:8090  # Traefik dashboard
```

### 7. 🔄 CI/CD Pipeline (`07-cicd-pipeline/`)

Complete GitHub Actions workflow for automated testing, security scanning, and deployment.

**Features:**
- Multi-stage pipeline (security scan → build → test → deploy)
- Parallel builds for all examples
- Container image security scanning
- SBOM generation and signing
- Integration testing
- Automated deployment to staging

**Setup:**
```bash
# Copy workflow to your repository
mkdir -p .github/workflows
cp 07-cicd-pipeline/ci-cd.yml .github/workflows/

# Run integration tests locally
./07-cicd-pipeline/integration-tests.sh

# The pipeline will automatically run on:
# - Push to main/develop branches
# - Pull requests to main
```

---

## 🛡️ Security Best Practices

This repository demonstrates several security best practices:

### Container Security
- ✅ **Non-root users** - All containers run as non-privileged users
- ✅ **Multi-stage builds** - Separate build and runtime environments
- ✅ **Minimal base images** - Using slim/alpine variants
- ✅ **Security scanning** - Automated vulnerability detection
- ✅ **SBOM generation** - Software Bill of Materials for compliance

### Application Security
- ✅ **API key authentication** - Secure API access
- ✅ **Input validation** - Proper request validation with Pydantic
- ✅ **Security headers** - CORS, CSP, and other security headers
- ✅ **Secret management** - Environment variable configuration
- ✅ **Health checks** - Proper monitoring and observability

### CI/CD Security
- ✅ **Automated security scans** - Trivy integration in CI pipeline
- ✅ **Container signing** - Cosign for container image attestation
- ✅ **SLSA provenance** - Supply chain security compliance
- ✅ **Dependency scanning** - Regular vulnerability updates

---

## 🔧 Development Setup

### Prerequisites
```bash
# Install required tools
brew install docker docker-compose
brew install trivy  # Security scanner
brew install syft   # SBOM generator

# For GPU support (optional)
# Install NVIDIA Docker runtime
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Environment Setup
```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Docker BuildKit (recommended)
export DOCKER_BUILDKIT=1
```

### Testing
```bash
# Run individual example tests
cd 01-basic-dockerfile
docker build -t test .
docker run --rm -p 8000:8000 test

# Run full integration test suite
./07-cicd-pipeline/integration-tests.sh

# Security scanning
cd 05-security-scans
./security-scan.sh your-image-name
```

---

## 🚀 Production Deployment

### Kubernetes Deployment
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-api
  template:
    metadata:
      labels:
        app: ai-api
    spec:
      containers:
      - name: ai-api
        image: ghcr.io/your-org/ai-api:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Docker Swarm
```bash
# Deploy to Docker Swarm
docker stack deploy -c docker-compose.yml ai-stack
```

### Cloud Deployment
- **AWS ECS**: Use task definitions with health checks
- **Google Cloud Run**: Deploy with proper CPU/memory limits
- **Azure Container Instances**: Configure with monitoring

---

## 📊 Monitoring and Observability

### Metrics and Logging
```bash
# View container logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Health check status
docker inspect --format='{{.State.Health}}' container-name
```

### Prometheus Integration
```yaml
# Add to docker-compose.yml for monitoring
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Contribution Guidelines
- Follow security best practices
- Add comprehensive documentation
- Include tests for new features
- Update README with new examples
- Ensure all CI checks pass

---

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent AI framework
- [LangChain](https://github.com/hwchase17/langchain) - LLM application framework
- [Trivy](https://github.com/aquasecurity/trivy) - Container security scanner
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern Python web framework
- [Docker](https://www.docker.com/) - Containerization platform

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/pragyakeshap/awesome-docker-experiments/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/pragyakeshap/awesome-docker-experiments/discussions)
- 📧 **Email**: pragya.rawal@gmail.com , pragyakeshap@gmail.com

---

**⭐ Star this repository if it helped you!**
