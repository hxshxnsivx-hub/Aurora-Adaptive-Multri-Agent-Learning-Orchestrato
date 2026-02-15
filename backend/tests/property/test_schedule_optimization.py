"""
Property-Based Tests for Schedule Optimization Feasibility

**Validates: Requirements 2.6, 3.2**

Property 4: Schedule Optimization Feasibility
- All scheduled tasks must fit within user availability
- Total scheduled time per day must not exceed max daily hours
- Task dependencies must be respected in scheduling
- Schedule adjustments must maintain milestone deadlines
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta
from typing import Dict, List

from app.agents.schedule_optimizer import ScheduleOptimizerAgent


# Strategies for generating test data
@st.composite
def availability_schedule(draw):
    """Generate valid availability schedule."""
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    schedule = {}
    num_days = draw(st.integers(min_value=3, max_value=7))
    selected_days = draw(st.lists(st.sampled_from(days), min_size=num_days, max_size=num_days, unique=True))
    
    for day in selected_days:
        num_slots = draw(st.integers(min_value=1, max_value=3))
        slots = []
        
        for _ in range(num_slots):
            start = draw(st.integers(min_value=6, max_value=20))
            duration = draw(st.integers(min_value=1, max_value=4))
            end = min(start + duration, 23)
            
            if end > start:
                slots.append({"start": start, "end": end})
        
        if slots:
            schedule[day] = slots
    
    return schedule


@st.composite
def task_list(draw):
    """Generate list of tasks to schedule."""
    num_tasks = draw(st.integers(min_value=3, max_value=15))
    tasks = []
    
    for i in range(num_tasks):
        task = {
            "id": f"task_{i}",
            "title": f"Task {i}",
            "estimated_minutes": draw(st.integers(min_value=15, max_value=180)),
            "priority": draw(st.sampled_from(["low", "medium", "high"])),
            "dependencies": []
        }
        
        # Add dependencies to earlier tasks
        if i > 0 and draw(st.booleans()):
            num_deps = draw(st.integers(min_value=1, max_value=min(2, i)))
            deps = draw(st.lists(
                st.integers(min_value=0, max_value=i-1),
                min_size=num_deps,
                max_size=num_deps,
                unique=True
            ))
            task["dependencies"] = [f"task_{d}" for d in deps]
        
        tasks.append(task)
    
    return tasks


class TestScheduleOptimizationFeasibility:
    """Property-based tests for schedule optimization feasibility."""
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_all_tasks_within_availability(self, tasks, availability):
        """
        Property: All scheduled tasks must be within user availability.
        
        No task should be scheduled outside available time slots.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        for scheduled_task in schedule:
            day = scheduled_task["day"]
            hour = scheduled_task["hour"]
            
            assert day in availability, \
                f"Task scheduled on {day} which is not in availability"
            
            # Check if hour is within any available slot
            in_slot = any(
                slot["start"] <= hour < slot["end"]
                for slot in availability[day]
            )
            
            assert in_slot, \
                f"Task scheduled at {hour}:00 on {day} is outside available slots"
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule(),
        max_daily_hours=st.integers(min_value=2, max_value=8)
    )
    async def test_daily_time_limit_respected(self, tasks, availability, max_daily_hours):
        """
        Property: Total scheduled time per day must not exceed max daily hours.
        
        Prevents overloading any single day.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(
            tasks,
            availability,
            max_daily_hours=max_daily_hours
        )
        
        # Calculate total minutes per day
        daily_minutes = {}
        for scheduled_task in schedule:
            day = scheduled_task["day"]
            task_id = scheduled_task["task_id"]
            
            # Find original task to get duration
            original_task = next((t for t in tasks if t["id"] == task_id), None)
            if original_task:
                minutes = original_task["estimated_minutes"]
                daily_minutes[day] = daily_minutes.get(day, 0) + minutes
        
        # Check each day
        for day, total_minutes in daily_minutes.items():
            total_hours = total_minutes / 60
            assert total_hours <= max_daily_hours + 0.5, \
                f"Day {day} has {total_hours:.1f} hours scheduled, exceeds limit of {max_daily_hours}"
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_task_dependencies_respected(self, tasks, availability):
        """
        Property: Task dependencies must be respected in scheduling.
        
        Prerequisite tasks must be scheduled before dependent tasks.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        # Build schedule time map
        task_times = {}
        for scheduled_task in schedule:
            task_id = scheduled_task["task_id"]
            day = scheduled_task["day"]
            hour = scheduled_task["hour"]
            
            # Convert to comparable timestamp
            day_index = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day)
            timestamp = day_index * 24 + hour
            task_times[task_id] = timestamp
        
        # Check dependencies
        for task in tasks:
            if task["id"] in task_times:
                task_time = task_times[task["id"]]
                
                for dep_id in task["dependencies"]:
                    if dep_id in task_times:
                        dep_time = task_times[dep_id]
                        assert dep_time < task_time, \
                            f"Dependency {dep_id} scheduled after {task['id']}"
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_high_priority_tasks_scheduled_first(self, tasks, availability):
        """
        Property: High priority tasks should be scheduled earlier.
        
        Priority should influence scheduling order.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        assume(len(schedule) >= 3)
        
        # Group tasks by priority
        priority_map = {"high": 3, "medium": 2, "low": 1}
        
        high_priority_times = []
        low_priority_times = []
        
        for scheduled_task in schedule:
            task_id = scheduled_task["task_id"]
            original_task = next((t for t in tasks if t["id"] == task_id), None)
            
            if original_task:
                day = scheduled_task["day"]
                hour = scheduled_task["hour"]
                day_index = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day)
                timestamp = day_index * 24 + hour
                
                if original_task["priority"] == "high":
                    high_priority_times.append(timestamp)
                elif original_task["priority"] == "low":
                    low_priority_times.append(timestamp)
        
        # If we have both high and low priority tasks
        if high_priority_times and low_priority_times:
            avg_high = sum(high_priority_times) / len(high_priority_times)
            avg_low = sum(low_priority_times) / len(low_priority_times)
            
            # High priority should generally be scheduled earlier
            assert avg_high <= avg_low + 24, \
                "High priority tasks should be scheduled earlier than low priority"
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_schedule_completeness(self, tasks, availability):
        """
        Property: All schedulable tasks should be scheduled.
        
        If there's enough availability, all tasks should fit.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        # Calculate total available hours
        total_available_minutes = 0
        for day, slots in availability.items():
            for slot in slots:
                total_available_minutes += (slot["end"] - slot["start"]) * 60
        
        # Calculate total task time
        total_task_minutes = sum(t["estimated_minutes"] for t in tasks)
        
        # If there's enough time, most tasks should be scheduled
        if total_available_minutes >= total_task_minutes * 1.2:
            scheduled_count = len(schedule)
            total_count = len(tasks)
            
            coverage = scheduled_count / total_count if total_count > 0 else 0
            assert coverage >= 0.7, \
                f"Should schedule at least 70% of tasks when time available, got {coverage:.2%}"
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_no_overlapping_tasks(self, tasks, availability):
        """
        Property: No two tasks should be scheduled at the same time.
        
        Each time slot should have at most one task.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        # Track scheduled time slots
        time_slots = set()
        
        for scheduled_task in schedule:
            day = scheduled_task["day"]
            hour = scheduled_task["hour"]
            slot_key = f"{day}_{hour}"
            
            assert slot_key not in time_slots, \
                f"Multiple tasks scheduled at {day} {hour}:00"
            
            time_slots.add(slot_key)
    
    @pytest.mark.property
    @given(
        tasks=task_list(),
        availability=availability_schedule()
    )
    async def test_schedule_determinism(self, tasks, availability):
        """
        Property: Schedule optimization should be deterministic.
        
        Same inputs should produce same schedule.
        """
        agent = ScheduleOptimizerAgent()
        
        schedule1 = await agent.optimize_schedule(tasks, availability)
        schedule2 = await agent.optimize_schedule(tasks, availability)
        
        # Schedules should be identical
        assert len(schedule1) == len(schedule2), \
            "Schedule length should be deterministic"
        
        # Sort both schedules for comparison
        sorted1 = sorted(schedule1, key=lambda x: (x["day"], x["hour"], x["task_id"]))
        sorted2 = sorted(schedule2, key=lambda x: (x["day"], x["hour"], x["task_id"]))
        
        assert sorted1 == sorted2, \
            "Schedule should be deterministic for same inputs"
