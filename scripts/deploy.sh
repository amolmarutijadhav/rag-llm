#!/bin/bash

# RAG LLM API Docker Deployment Script
# Supports both production and development deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/config/env.example"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your API keys and configuration"
        else
            print_error "Environment template not found at $ENV_EXAMPLE"
            exit 1
        fi
    else
        print_status "Environment file already exists"
    fi
}

# Function to create required directories
create_directories() {
    print_status "Creating required directories..."
    
    cd "$PROJECT_ROOT"
    mkdir -p logs temp certs htmlcov
    
    print_success "Created required directories"
}

# Function to build Docker images
build_images() {
    local target=${1:-production}
    print_status "Building Docker image for $target environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$target" = "development" ]; then
        docker-compose build --target development
    else
        docker-compose build --target production
    fi
    
    print_success "Docker image built successfully"
}

# Function to start services
start_services() {
    local environment=${1:-production}
    print_status "Starting services in $environment environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "development" ]; then
        docker-compose --profile dev up -d
        print_success "Development services started on port 8001"
    else
        docker-compose up -d
        print_success "Production services started on port 8000"
    fi
}

# Function to stop services
stop_services() {
    local environment=${1:-production}
    print_status "Stopping services in $environment environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "development" ]; then
        docker-compose --profile dev down
    else
        docker-compose down
    fi
    
    print_success "Services stopped"
}

# Function to show service status
show_status() {
    print_status "Checking service status..."
    
    cd "$PROJECT_ROOT"
    docker-compose ps
    
    echo ""
    print_status "Health check:"
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Production API is healthy"
    else
        print_warning "Production API health check failed"
    fi
    
    if curl -f http://localhost:8001/health &> /dev/null; then
        print_success "Development API is healthy"
    else
        print_warning "Development API health check failed"
    fi
}

# Function to show logs
show_logs() {
    local environment=${1:-production}
    print_status "Showing logs for $environment environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "development" ]; then
        docker-compose --profile dev logs -f
    else
        docker-compose logs -f
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    cd "$PROJECT_ROOT"
    
    # Stop all services
    docker-compose down --remove-orphans
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Cleanup completed"
}

# Function to run tests
run_tests() {
    print_status "Running tests in Docker container..."
    
    cd "$PROJECT_ROOT"
    
    # Run tests in development container
    docker-compose --profile dev run --rm rag-llm-api-dev python3 -m pytest tests/ -v
}

# Function to show help
show_help() {
    echo "RAG LLM API Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup           Setup environment and create directories"
    echo "  build           Build Docker images"
    echo "  start           Start services (production)"
    echo "  start-dev       Start services (development)"
    echo "  stop            Stop services (production)"
    echo "  stop-dev        Stop services (development)"
    echo "  restart         Restart services (production)"
    echo "  restart-dev     Restart services (development)"
    echo "  status          Show service status"
    echo "  logs            Show logs (production)"
    echo "  logs-dev        Show logs (development)"
    echo "  test            Run tests in Docker container"
    echo "  cleanup         Clean up Docker resources"
    echo "  deploy          Full deployment (setup + build + start)"
    echo "  deploy-dev      Full development deployment"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy       # Deploy production environment"
    echo "  $0 deploy-dev   # Deploy development environment"
    echo "  $0 logs         # Show production logs"
    echo "  $0 status       # Check service status"
}

# Main script logic
main() {
    local command=${1:-help}
    
    case $command in
        setup)
            check_prerequisites
            setup_environment
            create_directories
            ;;
        build)
            check_prerequisites
            build_images
            ;;
        start)
            check_prerequisites
            start_services production
            ;;
        start-dev)
            check_prerequisites
            start_services development
            ;;
        stop)
            stop_services production
            ;;
        stop-dev)
            stop_services development
            ;;
        restart)
            stop_services production
            start_services production
            ;;
        restart-dev)
            stop_services development
            start_services development
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs production
            ;;
        logs-dev)
            show_logs development
            ;;
        test)
            check_prerequisites
            run_tests
            ;;
        cleanup)
            cleanup
            ;;
        deploy)
            check_prerequisites
            setup_environment
            create_directories
            build_images production
            start_services production
            print_success "Production deployment completed!"
            print_status "API available at: http://localhost:8000"
            print_status "Health check: http://localhost:8000/health"
            print_status "API docs: http://localhost:8000/docs"
            ;;
        deploy-dev)
            check_prerequisites
            setup_environment
            create_directories
            build_images development
            start_services development
            print_success "Development deployment completed!"
            print_status "API available at: http://localhost:8001"
            print_status "Health check: http://localhost:8001/health"
            print_status "API docs: http://localhost:8001/docs"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 