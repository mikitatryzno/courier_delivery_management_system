#!/bin/bash

# Docker logs script

set -e

# Colors for output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Show logs for specific service
show_service_logs() {
    local service=$1
    local follow=${2:-false}
    
    if [ "$follow" = "true" ]; then
        print_status "Following logs for $service (Press Ctrl+C to stop)..."
        docker-compose logs -f $service
    else
        print_status "Showing recent logs for $service..."
        docker-compose logs --tail=50 $service
    fi
}

# Show logs for all services
show_all_logs() {
    local follow=${1:-false}
    
    if [ "$follow" = "true" ]; then
        print_status "Following logs for all services (Press Ctrl+C to stop)..."
        docker-compose logs -f
    else
        print_status "Showing recent logs for all services..."
        docker-compose logs --tail=20
    fi
}

# Main function
main() {
    local service=${1:-all}
    local follow=${2:-false}
    
    if [ "$service" = "all" ]; then
        show_all_logs $follow
    else
        show_service_logs $service $follow
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [service] [follow]"
    echo ""
    echo "Services:"
    echo "  all         Show logs for all services (default)"
    echo "  backend     Show backend logs"
    echo "  frontend    Show frontend logs"
    echo "  postgres    Show database logs"
    echo "  redis       Show Redis logs"
    echo "  pgadmin     Show pgAdmin logs"
    echo ""
    echo "Options:"
    echo "  follow      Follow logs in real-time"
    echo ""
    echo "Examples:"
    echo "  $0                    # Show recent logs for all services"
    echo "  $0 backend            # Show recent backend logs"
    echo "  $0 backend follow     # Follow backend logs"
    echo "  $0 all follow         # Follow all logs"
}

# Parse arguments
case "${1:-all}" in
    "backend"|"frontend"|"postgres"|"redis"|"pgadmin"|"all")
        if [ "$2" = "follow" ] || [ "$2" = "-f" ]; then
            main $1 true
        else
            main $1 false
        fi
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "Unknown service: $1"
        show_help
        exit 1
        ;;
esac