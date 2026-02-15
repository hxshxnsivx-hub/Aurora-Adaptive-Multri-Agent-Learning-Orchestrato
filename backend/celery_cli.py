#!/usr/bin/env python3
"""
Celery CLI management script for the Adaptive Learning Platform.
"""

import click
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.celery.worker import celery_app
from app.celery.management import celery_manager, get_task_monitoring_data
import json


@click.group()
def cli():
    """Celery management CLI for Adaptive Learning Platform."""
    pass


@cli.command()
@click.option('--loglevel', default='info', help='Logging level')
@click.option('--concurrency', default=4, help='Number of concurrent worker processes')
@click.option('--queues', default='celery', help='Comma-separated list of queues to consume')
def worker(loglevel, concurrency, queues):
    """Start Celery worker."""
    click.echo(f"Starting Celery worker with {concurrency} processes...")
    click.echo(f"Queues: {queues}")
    click.echo(f"Log level: {loglevel}")
    
    celery_app.worker_main([
        'worker',
        f'--loglevel={loglevel}',
        f'--concurrency={concurrency}',
        f'--queues={queues}',
        '--without-gossip',
        '--without-mingle',
        '--without-heartbeat'
    ])


@cli.command()
@click.option('--loglevel', default='info', help='Logging level')
def beat(loglevel):
    """Start Celery beat scheduler."""
    click.echo("Starting Celery beat scheduler...")
    click.echo(f"Log level: {loglevel}")
    
    celery_app.start([
        'celery',
        'beat',
        f'--loglevel={loglevel}',
        '--pidfile=/tmp/celerybeat.pid'
    ])


@cli.command()
@click.option('--loglevel', default='info', help='Logging level')
def flower(loglevel):
    """Start Flower monitoring server."""
    click.echo("Starting Flower monitoring server...")
    click.echo("Access at: http://localhost:5555")
    
    os.system(f"celery -A app.celery.worker flower --loglevel={loglevel}")


@cli.command()
def status():
    """Show worker status and statistics."""
    click.echo("=== Celery Worker Status ===")
    
    stats = celery_manager.get_worker_stats()
    if not stats:
        click.echo("No workers found or workers are not responding.")
        return
    
    for worker_name, worker_stats in stats.items():
        click.echo(f"\nWorker: {worker_name}")
        click.echo(f"  Status: Active")
        
        if 'pool' in worker_stats:
            pool_info = worker_stats['pool']
            click.echo(f"  Processes: {pool_info.get('processes', 'N/A')}")
            click.echo(f"  Max concurrency: {pool_info.get('max-concurrency', 'N/A')}")
        
        if 'rusage' in worker_stats:
            rusage = worker_stats['rusage']
            click.echo(f"  CPU time: {rusage.get('utime', 0):.2f}s")
            click.echo(f"  Memory: {rusage.get('maxrss', 0)} KB")


@cli.command()
def active():
    """Show active tasks."""
    click.echo("=== Active Tasks ===")
    
    active_tasks = celery_manager.get_active_tasks()
    if not active_tasks:
        click.echo("No active tasks.")
        return
    
    for worker_name, tasks in active_tasks.items():
        if tasks:
            click.echo(f"\nWorker: {worker_name}")
            for task in tasks:
                click.echo(f"  Task: {task.get('name', 'Unknown')}")
                click.echo(f"    ID: {task.get('id', 'N/A')}")
                click.echo(f"    Args: {task.get('args', [])}")
                click.echo(f"    Started: {task.get('time_start', 'N/A')}")


@cli.command()
def scheduled():
    """Show scheduled tasks."""
    click.echo("=== Scheduled Tasks ===")
    
    scheduled_tasks = celery_manager.get_scheduled_tasks()
    if not scheduled_tasks:
        click.echo("No scheduled tasks.")
        return
    
    for worker_name, tasks in scheduled_tasks.items():
        if tasks:
            click.echo(f"\nWorker: {worker_name}")
            for task in tasks:
                click.echo(f"  Task: {task.get('request', {}).get('task', 'Unknown')}")
                click.echo(f"    ID: {task.get('request', {}).get('id', 'N/A')}")
                click.echo(f"    ETA: {task.get('eta', 'N/A')}")


@cli.command()
@click.argument('task_id')
def result(task_id):
    """Get task result by ID."""
    click.echo(f"=== Task Result: {task_id} ===")
    
    result = celery_manager.get_task_result(task_id)
    if result:
        click.echo(f"Status: {result['status']}")
        click.echo(f"Result: {json.dumps(result['result'], indent=2)}")
        if result['date_done']:
            click.echo(f"Completed: {result['date_done']}")
        if result['traceback']:
            click.echo(f"Error: {result['traceback']}")
    else:
        click.echo("Task not found or result unavailable.")


@cli.command()
@click.argument('task_id')
@click.option('--terminate', is_flag=True, help='Terminate the task immediately')
def revoke(task_id, terminate):
    """Revoke a task by ID."""
    success = celery_manager.revoke_task(task_id, terminate=terminate)
    if success:
        action = "terminated" if terminate else "revoked"
        click.echo(f"Task {task_id} {action} successfully.")
    else:
        click.echo(f"Failed to revoke task {task_id}.")


@cli.command()
@click.option('--queue', default='celery', help='Queue to purge')
@click.confirmation_option(prompt='Are you sure you want to purge all tasks?')
def purge(queue):
    """Purge all tasks from a queue."""
    purged = celery_manager.purge_queue(queue)
    click.echo(f"Purged {purged} tasks from queue '{queue}'.")


@cli.command()
def health():
    """Show system health metrics."""
    click.echo("=== System Health ===")
    
    health = celery_manager.get_system_health()
    click.echo(f"Health Score: {health.get('health_score', 0):.2f}")
    click.echo(f"Timestamp: {health.get('timestamp', 'N/A')}")
    
    if 'workers' in health:
        workers = health['workers']
        click.echo(f"\nWorkers:")
        click.echo(f"  Total: {workers.get('total', 0)}")
        click.echo(f"  Active: {workers.get('active', 0)}")
    
    if 'tasks' in health:
        tasks = health['tasks']
        click.echo(f"\nTasks:")
        click.echo(f"  Active: {tasks.get('active', 0)}")
        click.echo(f"  Scheduled: {tasks.get('scheduled', 0)}")
    
    if 'performance' in health:
        perf = health['performance']
        click.echo(f"\nPerformance:")
        click.echo(f"  Average Load: {perf.get('average_load', 0):.2f}")
        click.echo(f"  Memory Usage: {perf.get('memory_usage', 'N/A')}")


@cli.command()
def monitor():
    """Get comprehensive monitoring data (JSON output)."""
    data = get_task_monitoring_data()
    click.echo(json.dumps(data, indent=2, default=str))


@cli.command()
def registered():
    """Show registered tasks."""
    click.echo("=== Registered Tasks ===")
    
    registered = celery_manager.get_registered_tasks()
    if not registered:
        click.echo("No registered tasks found.")
        return
    
    for worker_name, tasks in registered.items():
        click.echo(f"\nWorker: {worker_name}")
        for task in sorted(tasks):
            click.echo(f"  - {task}")


@cli.command()
@click.argument('task_name')
@click.argument('args', nargs=-1)
def run(task_name, args):
    """Run a task manually."""
    click.echo(f"Running task: {task_name}")
    click.echo(f"Arguments: {args}")
    
    try:
        # Convert string args to appropriate types
        parsed_args = []
        for arg in args:
            try:
                # Try to parse as JSON first
                parsed_args.append(json.loads(arg))
            except json.JSONDecodeError:
                # If not JSON, keep as string
                parsed_args.append(arg)
        
        result = celery_app.send_task(task_name, args=parsed_args)
        click.echo(f"Task queued with ID: {result.id}")
        click.echo("Use 'celery_cli.py result <task_id>' to check the result.")
        
    except Exception as e:
        click.echo(f"Error running task: {e}")


if __name__ == '__main__':
    cli()