# Celery Background Processing Setup

This document describes the Celery background job processing system for the Adaptive Learning Platform.

## Overview

The platform uses Celery with Redis as the message broker for handling background tasks including:

- **Resource Curation**: Discovering and ranking educational content
- **Learning Path Generation**: Creating personalized learning paths
- **Integration Synchronization**: Syncing with Google Calendar and Notion
- **Analytics Processing**: Calculating user metrics and insights
- **System Maintenance**: Cleanup and optimization tasks

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Worker  │    │  Celery Beat    │
│                 │    │                 │    │   (Scheduler)   │
│  - Submit Tasks │    │  - Execute Tasks│    │  - Periodic     │
│  - Monitor      │    │  - Report Status│    │    Tasks        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │      Redis      │
                    │                 │
                    │  - Message      │
                    │    Broker       │
                    │  - Result       │
                    │    Backend      │
                    │  - Cache        │
                    └─────────────────┘
```

## Task Categories

### 1. Resource Curation Tasks (`app.celery.tasks.resource_curation`)

- `discover_new_resources()`: Find new educational content
- `curate_resources_for_milestone(milestone_id)`: Curate content for specific milestones
- `update_resource_quality_scores()`: Update resource quality based on feedback

### 2. Path Generation Tasks (`app.celery.tasks.path_generation`)

- `generate_learning_path(user_id, goals, preferences)`: Create personalized learning paths
- `optimize_learning_schedule(user_id, path_id)`: Optimize scheduling
- `reallocate_learning_path(user_id, path_id, feedback)`: Adjust paths based on feedback
- `validate_learning_path(path_id)`: Validate path structure

### 3. Integration Sync Tasks (`app.celery.tasks.integration_sync`)

- `sync_google_calendar(user_id)`: Sync with Google Calendar
- `sync_notion_workspace(user_id)`: Sync with Notion
- `sync_all_integrations()`: Bulk sync for all users
- `handle_integration_webhook(type, user_id, data)`: Handle webhooks
- `refresh_integration_tokens()`: Refresh OAuth tokens

### 4. Analytics Tasks (`app.celery.tasks.analytics`)

- `update_daily_analytics()`: Calculate daily metrics
- `calculate_user_performance_metrics(user_id)`: User-specific metrics
- `generate_learning_insights(user_id)`: Personalized insights
- `update_resource_analytics()`: Resource effectiveness metrics
- `generate_system_health_report()`: System health monitoring
- `cleanup_old_analytics_data()`: Data maintenance

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/adaptive_learning
```

### Celery Settings

- **Task Time Limit**: 30 minutes (hard limit)
- **Soft Time Limit**: 25 minutes
- **Worker Prefetch**: 1 task per worker
- **Max Tasks per Child**: 1000 tasks
- **Result Expiry**: 1 hour
- **Timezone**: UTC

## Running Celery Services

### Using Docker Compose (Recommended)

```bash
# Start all services including Celery
docker-compose up -d

# View Celery worker logs
docker-compose logs -f celery_worker

# View Celery beat logs
docker-compose logs -f celery_beat

# Access Flower monitoring
open http://localhost:5555
```

### Using CLI Scripts

```bash
# Start all Celery services
./scripts/start_celery.sh

# Stop all Celery services
./scripts/stop_celery.sh

# Start individual services
python celery_cli.py worker --loglevel=info --concurrency=4
python celery_cli.py beat --loglevel=info
python celery_cli.py flower --loglevel=info
```

### Manual Commands

```bash
# Start worker
celery -A app.celery.worker worker --loglevel=info

# Start beat scheduler
celery -A app.celery.worker beat --loglevel=info

# Start flower monitoring
celery -A app.celery.worker flower
```

## Management and Monitoring

### CLI Management

```bash
# Check worker status
python celery_cli.py status

# View active tasks
python celery_cli.py active

# View scheduled tasks
python celery_cli.py scheduled

# Get task result
python celery_cli.py result <task_id>

# Revoke a task
python celery_cli.py revoke <task_id> --terminate

# Purge queue
python celery_cli.py purge --queue celery

# System health
python celery_cli.py health

# Run task manually
python celery_cli.py run app.celery.tasks.analytics.update_daily_analytics
```

### API Endpoints

The platform provides REST API endpoints for task management:

- `GET /api/v1/tasks/health` - System health metrics
- `GET /api/v1/tasks/monitoring` - Comprehensive monitoring data
- `GET /api/v1/tasks/active` - Active tasks
- `GET /api/v1/tasks/scheduled` - Scheduled tasks
- `GET /api/v1/tasks/{task_id}/result` - Task result
- `POST /api/v1/tasks/submit` - Submit new task
- `POST /api/v1/tasks/{task_id}/revoke` - Revoke task
- `POST /api/v1/tasks/learning-path/generate` - Generate learning path
- `POST /api/v1/tasks/integrations/sync` - Sync integrations

### Flower Web Interface

Access the Flower monitoring interface at `http://localhost:5555` to:

- Monitor worker status and performance
- View task history and results
- Inspect task details and tracebacks
- Monitor queue lengths and throughput
- View worker resource usage

## Periodic Tasks

The system runs several periodic tasks automatically:

| Task | Frequency | Description |
|------|-----------|-------------|
| Integration Sync | 5 minutes | Sync all user integrations |
| Daily Analytics | 1 hour | Update user analytics |
| Resource Discovery | 30 minutes | Find new educational content |
| Resource Quality Update | 2 hours | Update resource quality scores |
| Token Refresh | 6 hours | Refresh OAuth tokens |
| Resource Analytics | 4 hours | Update resource effectiveness |
| Health Report | Daily | Generate system health report |
| Data Cleanup | Weekly | Clean old analytics data |

## Error Handling and Retry Logic

### Automatic Retries

Tasks automatically retry on failure with exponential backoff:

- **Max Retries**: 3 attempts
- **Retry Delay**: Exponential backoff (2^retry_count seconds)
- **Retry Conditions**: Network errors, temporary API failures

### Error Monitoring

- All task failures are logged with full tracebacks
- Failed tasks can be retried manually via API or CLI
- System health monitoring tracks error rates
- Sentry integration for production error tracking

## Performance Optimization

### Scaling Workers

```bash
# Scale workers horizontally
docker-compose up -d --scale celery_worker=4

# Or adjust concurrency
python celery_cli.py worker --concurrency=8
```

### Queue Management

```bash
# Monitor queue lengths
python celery_cli.py monitor | jq '.queue_lengths'

# Purge stuck tasks
python celery_cli.py purge --queue celery
```

### Memory Management

- Workers restart after 1000 tasks to prevent memory leaks
- Task results expire after 1 hour
- Old analytics data is cleaned weekly

## Development and Testing

### Running Tests

```bash
# Test Celery tasks
pytest tests/test_celery_tasks.py

# Test with actual Redis
pytest tests/test_celery_integration.py
```

### Development Mode

```bash
# Start with auto-reload
python celery_cli.py worker --loglevel=debug --concurrency=1

# Monitor task execution
tail -f logs/celery_worker.log
```

## Production Deployment

### Scaling Considerations

- Use multiple worker processes (4-8 per CPU core)
- Separate queues for different task types
- Use Redis Cluster for high availability
- Monitor memory usage and scale accordingly

### Security

- Use Redis AUTH in production
- Encrypt sensitive task arguments
- Implement proper access controls for Flower
- Use SSL/TLS for Redis connections

### Monitoring

- Set up Prometheus metrics collection
- Configure alerting for failed tasks
- Monitor queue lengths and processing times
- Track worker health and resource usage

## Troubleshooting

### Common Issues

1. **Workers not starting**
   - Check Redis connection
   - Verify Python path and dependencies
   - Check log files for errors

2. **Tasks not executing**
   - Verify task registration
   - Check queue names
   - Monitor worker logs

3. **High memory usage**
   - Reduce worker concurrency
   - Increase max_tasks_per_child
   - Monitor task memory usage

4. **Slow task processing**
   - Scale workers horizontally
   - Optimize task code
   - Check Redis performance

### Debug Commands

```bash
# Check Redis connection
redis-cli ping

# Inspect Celery configuration
python -c "from app.celery.worker import celery_app; print(celery_app.conf)"

# Test task execution
python celery_cli.py run app.celery.tasks.analytics.update_daily_analytics

# Monitor system resources
python celery_cli.py health
```

## Contributing

When adding new Celery tasks:

1. Create tasks in appropriate module (`resource_curation`, `path_generation`, etc.)
2. Add task to periodic schedule if needed
3. Update API endpoints for user-facing tasks
4. Add tests for task functionality
5. Update this documentation

For more information, see the main project documentation.