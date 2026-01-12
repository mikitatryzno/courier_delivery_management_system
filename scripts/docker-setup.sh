#!/bin/bash

# Docker setup script for Courier Delivery Management System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p database/init
    
    print_success "Directories created"
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    if [ ! -f .env ]; then
        if [ "$1" = "dev" ]; then
            cp .env.docker.dev .env
            print_success "Development environment file created"
        else
            cp .env.docker .env
            print_warning "Production environment file created. Please update the SECRET_KEY!"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Build and start services
start_services() {
    local mode=$1
    
    if [ "$mode" = "dev" ]; then
        print_status "Starting development services..."
        docker-compose -f docker-compose.dev.yml up --build -d
    else
        print_status "Starting production services..."
        docker-compose up --build -d
    fi
    
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend to be healthy
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            print_success "Backend service is ready"
            break
        fi
        
        print_status "Waiting for backend... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Backend service failed to start"
        exit 1
    fi
    
    # Wait for frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend service is ready"
    else
        print_warning "Frontend service may not be ready yet"
    fi
}

# Show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Available Services:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/api/health"
    
    if docker-compose ps | grep -q pgadmin; then
        echo "  - pgAdmin: http://localhost:5050"
    fi
}

# Main function
main() {
    local mode=${1:-prod}
    
    echo "=========================================="
    echo "Courier Delivery Management System Setup"
    echo "=========================================="
    
    check_docker
    create_directories
    setup_env_files $mode
    start_services $mode
    wait_for_services
    show_status
    
    print_success "Setup completed successfully!"
    
    if [ "$mode" = "prod" ]; then
        print_warning "Don't forget to update the SECRET_KEY in .env file for production!"
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  prod    Start production services (default)"
    echo "  dev     Start development services"
    echo "  help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0          # Start production services"
    echo "  $0 dev      # Start development services"
    echo "  $0 help     # Show help"
}

# Parse arguments
case "${1:-prod}" in
    "prod")
        main prod
        ;;
    "dev")
        main dev
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown mode: $1"
        show_help
        exit 1
        ;;
esac