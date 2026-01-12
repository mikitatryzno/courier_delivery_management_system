#!/bin/bash

# Docker cleanup script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Stop and remove containers
stop_services() {
    print_status "Stopping services..."
    
    if [ -f docker-compose.yml ]; then
        docker-compose down
    fi
    
    if [ -f docker-compose.dev.yml ]; then
        docker-compose -f docker-compose.dev.yml down
    fi
    
    print_success "Services stopped"
}

# Remove containers and images
cleanup_containers() {
    print_status "Cleaning up containers and images..."
    
    # Remove containers
    docker container prune -f
    
    # Remove images
    docker image prune -f
    
    # Remove courier-delivery related images
    docker images | grep courier | awk '{print $3}' | xargs -r docker rmi -f
    
    print_success "Containers and images cleaned up"
}

# Remove volumes (optional)
cleanup_volumes() {
    if [ "$1" = "volumes" ]; then
        print_warning "This will remove all data including database!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing volumes..."
            docker volume prune -f
            print_success "Volumes removed"
        else
            print_status "Volumes preserved"
        fi
    fi
}

# Remove networks
cleanup_networks() {
    print_status "Cleaning up networks..."
    docker network prune -f
    print_success "Networks cleaned up"
}

# Main cleanup function
main() {
    echo "========================================"
    echo "Courier Delivery System Cleanup"
    echo "========================================"
    
    stop_services
    cleanup_containers
    cleanup_volumes $1
    cleanup_networks
    
    print_success "Cleanup completed!"
}

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  volumes    Also remove volumes (WARNING: This will delete all data!)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Clean up containers, images, and networks"
    echo "  $0 volumes      # Clean up everything including data volumes"
}

# Parse arguments
case "${1:-}" in
    "volumes")
        main volumes
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac