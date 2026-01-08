#!/bin/bash
# Quick Docker Compose management script for Tank Simulator

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-help}" in
  up)
    echo "🚀 Starting Tank Simulator (MongoDB + App)..."
    docker-compose up -d
    echo "✅ Services started!"
    echo "📍 API: http://localhost:8000"
    echo "📍 Docs: http://localhost:8000/docs"
    echo "📍 MongoDB: mongodb://mongo:mongo@localhost:27017/?authSource=admin"
    ;;
  down)
    echo "🛑 Stopping Tank Simulator..."
    docker-compose down
    echo "✅ Services stopped (data persisted)"
    ;;
  logs)
    echo "📋 Showing logs..."
    docker-compose logs -f
    ;;
  logs-app)
    echo "📋 Showing app logs..."
    docker-compose logs -f app
    ;;
  logs-mongo)
    echo "📋 Showing MongoDB logs..."
    docker-compose logs -f mongo
    ;;
  rebuild)
    echo "🔨 Rebuilding containers..."
    docker-compose build --no-cache
    echo "✅ Rebuild complete!"
    ;;
  restart)
    echo "🔄 Restarting services..."
    docker-compose restart
    echo "✅ Services restarted!"
    ;;
  status)
    echo "📊 Service status:"
    docker-compose ps
    ;;
  clean)
    echo "🗑️  Removing all containers and volumes (WARNING: deletes MongoDB data)..."
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    if [ "$confirm" = "yes" ]; then
      docker-compose down -v
      echo "✅ Cleaned up!"
    else
      echo "❌ Cancelled"
    fi
    ;;
  mongo)
    echo "🗄️  Connecting to MongoDB..."
    docker exec -it tank_simulator_mongo mongosh -u mongo -p mongo --authenticationDatabase admin
    ;;
  bash)
    echo "🔧 Opening bash in app container..."
    docker exec -it tank_simulator_app bash
    ;;
  *)
    echo "Tank Simulator Docker Manager"
    echo ""
    echo "Usage: $0 {command}"
    echo ""
    echo "Commands:"
    echo "  up            - Start all services"
    echo "  down          - Stop all services (keeps data)"
    echo "  logs          - View all logs"
    echo "  logs-app      - View app logs"
    echo "  logs-mongo    - View MongoDB logs"
    echo "  rebuild       - Rebuild containers from scratch"
    echo "  restart       - Restart services"
    echo "  status        - Show service status"
    echo "  mongo         - Connect to MongoDB shell"
    echo "  bash          - Open bash in app container"
    echo "  clean         - Remove all containers and volumes (DELETES DATA)"
    echo ""
    echo "Examples:"
    echo "  $0 up              # Start services"
    echo "  $0 logs            # Watch logs"
    echo "  $0 mongo           # Connect to MongoDB"
    exit 1
    ;;
esac

