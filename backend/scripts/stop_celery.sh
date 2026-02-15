#!/bin/bash

# Stop script for Celery services

echo "Stopping Celery services..."

# Function to stop process by PID file
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force stopping $service_name..."
                kill -9 "$pid"
            fi
            
            echo "$service_name stopped."
        else
            echo "$service_name was not running."
        fi
        rm -f "$pid_file"
    else
        echo "No PID file found for $service_name."
    fi
}

# Stop all services
stop_process "logs/celery_worker.pid" "Celery Worker"
stop_process "logs/celery_beat.pid" "Celery Beat"
stop_process "logs/celery_flower.pid" "Flower Monitoring"

# Also try to stop any remaining celery processes
echo "Cleaning up any remaining Celery processes..."
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "celery.*beat" 2>/dev/null || true
pkill -f "flower" 2>/dev/null || true

echo "All Celery services stopped."