#!/bin/bash

# Startup script for Celery services in development

echo "Starting Celery services for Adaptive Learning Platform..."

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Error: Redis is not running. Please start Redis first."
    echo "You can start Redis with: redis-server"
    exit 1
fi

# Create log directory
mkdir -p logs

# Start Celery worker in background
echo "Starting Celery worker..."
python celery_cli.py worker --loglevel=info --concurrency=4 > logs/celery_worker.log 2>&1 &
WORKER_PID=$!
echo "Celery worker started with PID: $WORKER_PID"

# Start Celery beat in background
echo "Starting Celery beat scheduler..."
python celery_cli.py beat --loglevel=info > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo "Celery beat started with PID: $BEAT_PID"

# Start Flower monitoring in background
echo "Starting Flower monitoring..."
python celery_cli.py flower --loglevel=info > logs/celery_flower.log 2>&1 &
FLOWER_PID=$!
echo "Flower monitoring started with PID: $FLOWER_PID"
echo "Access Flower at: http://localhost:5555"

# Save PIDs to file for easy cleanup
echo "$WORKER_PID" > logs/celery_worker.pid
echo "$BEAT_PID" > logs/celery_beat.pid
echo "$FLOWER_PID" > logs/celery_flower.pid

echo ""
echo "All Celery services started successfully!"
echo "Logs are available in the logs/ directory"
echo ""
echo "To stop all services, run: ./scripts/stop_celery.sh"
echo "To check status, run: python celery_cli.py status"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt signal
trap 'echo "Stopping Celery services..."; kill $WORKER_PID $BEAT_PID $FLOWER_PID; exit 0' INT
wait