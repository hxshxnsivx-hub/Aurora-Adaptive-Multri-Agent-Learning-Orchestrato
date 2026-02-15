"""
Unit tests for AI agents.
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.agents.orchestrator import CentralOrchestrator
from app.agents.context_analyzer import ContextAnalyzerAgent
from app.agents.user_profile import UserProfileAgent
from app.agents.goal_interpreter import GoalInterpreterAgent
from app.agents.path_planner import PathPlannerAgent
from app.agents.schedule_optimizer import ScheduleOptimizerAgent
from app.agents.research import ResearchAgent
from app.agents.resource_curator import ResourceCuratorAgent
from app.agents.task_manager import TaskManagerAgent
from app.agents.calendar import CalendarAgent
from app.agents.notion_sync import NotionSyncAgent
from app.agents.voice_assistant import VoiceAssistantAgent
from app.agents.reallocation import ReallocationAgent
from app.agents.base import AgentMessage, AgentState


class TestCentralOrchestrator:
    """Tests for Central Orchestrator Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = CentralOrchestrator()
        
        assert orchestrator.agent_id == "central_orchestrator"
        assert orchestrator.name == "Central Orchestrator"
        assert len(orchestrator.sub_agents) > 0
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_orchestrator_routes_path_generation(self, mock_agent_message, mock_agent_state):
        """Test orchestrator routes path generation requests correctly."""
        orchestrator = CentralOrchestrator()
        
        message = AgentMessage(
            sender="user",
            receiver="central_orchestrator",
            message_type="request",
            content={
                "action": "generate_path",
                "user_id": str(uuid4()),
                "goals": ["Learn Python"]
            }
        )
        
        response = await orchestrator.process(message, mock_agent_state)
        
        assert response is not None
        assert response.message_type in ["response", "error"]


class TestContextAnalyzerAgent:
    """Tests for Context Analyzer Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_context_analyzer_initialization(self):
        """Test context analyzer initializes correctly."""
        agent = ContextAnalyzerAgent()
        
        assert agent.agent_id == "context_analyzer"
        assert agent.name == "Context Analyzer"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_analyze_user_context(self, mock_agent_state):
        """Test context analysis for user."""
        agent = ContextAnalyzerAgent()
        
        message = AgentMessage(
            sender="orchestrator",
            receiver="context_analyzer",
            message_type="request",
            content={
                "action": "analyze_context",
                "user_id": str(uuid4()),
                "recent_activity": []
            }
        )
        
        response = await agent.process(message, mock_agent_state)
        
        assert response is not None
        assert "context" in response.content or "error" in response.content


class TestUserProfileAgent:
    """Tests for User Profile Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_user_profile_initialization(self):
        """Test user profile agent initializes correctly."""
        agent = UserProfileAgent()
        
        assert agent.agent_id == "user_profile"
        assert agent.name == "User Profile Agent"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_get_user_profile(self, mock_agent_state):
        """Test retrieving user profile."""
        agent = UserProfileAgent()
        
        message = AgentMessage(
            sender="orchestrator",
            receiver="user_profile",
            message_type="request",
            content={
                "action": "get_profile",
                "user_id": str(uuid4())
            }
        )
        
        response = await agent.process(message, mock_agent_state)
        
        assert response is not None
        assert response.message_type in ["response", "error"]
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_calculate_proficiency_bounds(self):
        """Test proficiency calculation stays within bounds."""
        agent = UserProfileAgent()
        
        questions = [
            {
                "id": "q1",
                "skill_domain": "python",
                "difficulty": 0.5,
                "correct_answer": "A"
            }
        ]
        
        responses = [
            {
                "question_id": "q1",
                "user_answer": "A",
                "time_taken": 60
            }
        ]
        
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        for skill, level in proficiency.items():
            assert 0.0 <= level <= 1.0, f"Proficiency must be in [0.0, 1.0], got {level}"


class TestGoalInterpreterAgent:
    """Tests for Goal Interpreter Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_goal_interpreter_initialization(self):
        """Test goal interpreter initializes correctly."""
        agent = GoalInterpreterAgent()
        
        assert agent.agent_id == "goal_interpreter"
        assert agent.name == "Goal Interpreter"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_interpret_learning_goals(self, mock_agent_state):
        """Test interpreting user learning goals."""
        agent = GoalInterpreterAgent()
        
        message = AgentMessage(
            sender="orchestrator",
            receiver="goal_interpreter",
            message_type="request",
            content={
                "action": "interpret_goals",
                "goals": ["I want to learn Python for data science"]
            }
        )
        
        response = await agent.process(message, mock_agent_state)
        
        assert response is not None
        assert response.message_type in ["response", "error"]


class TestPathPlannerAgent:
    """Tests for Path Planner Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_path_planner_initialization(self):
        """Test path planner initializes correctly."""
        agent = PathPlannerAgent()
        
        assert agent.agent_id == "path_planner"
        assert agent.name == "Path Planner"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_generate_learning_path(self):
        """Test generating a learning path."""
        agent = PathPlannerAgent()
        
        user_profile = {
            "skill_levels": {"python": 0.3},
            "weekly_hours": 10
        }
        
        goals = [
            {
                "skill": "python",
                "target_level": 0.8,
                "description": "Master Python"
            }
        ]
        
        path = await agent.generate_path(user_profile, goals)
        
        assert "id" in path
        assert "milestones" in path
        assert len(path["milestones"]) > 0


class TestScheduleOptimizerAgent:
    """Tests for Schedule Optimizer Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_schedule_optimizer_initialization(self):
        """Test schedule optimizer initializes correctly."""
        agent = ScheduleOptimizerAgent()
        
        assert agent.agent_id == "schedule_optimizer"
        assert agent.name == "Schedule Optimizer"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_optimize_schedule_respects_availability(self):
        """Test schedule optimization respects user availability."""
        agent = ScheduleOptimizerAgent()
        
        tasks = [
            {
                "id": str(uuid4()),
                "title": "Learn Python Basics",
                "estimated_minutes": 60
            }
        ]
        
        availability = {
            "monday": [{"start": 9, "end": 12}],
            "tuesday": [{"start": 14, "end": 17}]
        }
        
        schedule = await agent.optimize_schedule(tasks, availability)
        
        assert len(schedule) > 0
        
        # Verify all scheduled times are within availability
        for scheduled_task in schedule:
            day = scheduled_task["day"]
            hour = scheduled_task["hour"]
            
            assert day in availability
            
            # Check if hour is within any available slot
            in_slot = any(
                slot["start"] <= hour < slot["end"]
                for slot in availability[day]
            )
            assert in_slot, f"Scheduled hour {hour} not in availability for {day}"


class TestResearchAgent:
    """Tests for Research Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_research_agent_initialization(self):
        """Test research agent initializes correctly."""
        agent = ResearchAgent()
        
        assert agent.agent_id == "research"
        assert agent.name == "Research Agent"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_search_resources(self, mock_agent_state):
        """Test searching for resources."""
        agent = ResearchAgent()
        
        message = AgentMessage(
            sender="orchestrator",
            receiver="research",
            message_type="request",
            content={
                "action": "search_resources",
                "topics": ["python", "programming"],
                "difficulty": "beginner"
            }
        )
        
        response = await agent.process(message, mock_agent_state)
        
        assert response is not None
        assert response.message_type in ["response", "error"]


class TestResourceCuratorAgent:
    """Tests for Resource Curator Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_resource_curator_initialization(self):
        """Test resource curator initializes correctly."""
        agent = ResourceCuratorAgent()
        
        assert agent.agent_id == "resource_curator"
        assert agent.name == "Resource Curator"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_rank_resources(self):
        """Test ranking resources by quality."""
        agent = ResourceCuratorAgent()
        
        resources = [
            {
                "id": str(uuid4()),
                "title": "Python Tutorial",
                "quality_score": 0.8,
                "relevance_score": 0.9
            },
            {
                "id": str(uuid4()),
                "title": "Python Guide",
                "quality_score": 0.6,
                "relevance_score": 0.7
            }
        ]
        
        ranked = await agent.rank_resources(resources)
        
        assert len(ranked) == 2
        # Higher quality should be ranked first
        assert ranked[0]["quality_score"] >= ranked[1]["quality_score"]


class TestTaskManagerAgent:
    """Tests for Task Manager Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_task_manager_initialization(self):
        """Test task manager initializes correctly."""
        agent = TaskManagerAgent()
        
        assert agent.agent_id == "task_manager"
        assert agent.name == "Task Manager"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_create_tasks_from_milestone(self):
        """Test creating tasks from milestone."""
        agent = TaskManagerAgent()
        
        milestone = {
            "id": str(uuid4()),
            "title": "Python Basics",
            "topics": ["variables", "functions", "loops"],
            "estimated_hours": 10
        }
        
        tasks = await agent.create_tasks_from_milestone(milestone)
        
        assert len(tasks) > 0
        assert all("id" in task for task in tasks)
        assert all("title" in task for task in tasks)


class TestReallocationAgent:
    """Tests for Reallocation Agent."""
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_reallocation_agent_initialization(self):
        """Test reallocation agent initializes correctly."""
        agent = ReallocationAgent()
        
        assert agent.agent_id == "reallocation"
        assert agent.name == "Reallocation Agent"
    
    @pytest.mark.unit
    @pytest.mark.agent
    async def test_reallocate_path_preserves_goals(self):
        """Test reallocation preserves learning goals."""
        agent = ReallocationAgent()
        
        original_path = {
            "id": str(uuid4()),
            "goals": ["Master Python", "Learn Web Dev"],
            "milestones": [
                {"id": str(uuid4()), "title": "Python Basics", "difficulty_level": "beginner"}
            ]
        }
        
        feedback = {
            "reason": "too_easy",
            "current_milestone_id": original_path["milestones"][0]["id"]
        }
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        # Goals must be preserved
        assert new_path["goals"] == original_path["goals"]
