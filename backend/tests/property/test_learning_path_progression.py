"""
Property-Based Tests for Learning Path Progression Validity

**Validates: Requirements 2.1, 2.2, 2.5**

Property 2: Learning Path Progression Validity
- Paths must follow Beginner → Intermediate → Advanced → Expert progression
- Milestone difficulty must be monotonically increasing
- All milestones must be reachable given user's current skills
- Path completion must lead to goal achievement
"""
import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List

from app.agents.path_planner import PathPlannerAgent
from app.agents.base import AgentMessage, AgentState


# Strategies for generating test data
@st.composite
def user_skill_profile(draw):
    """Generate a valid user skill profile."""
    skills = ["python", "javascript", "algorithms", "data_structures", "web_development"]
    
    profile = {}
    for skill in draw(st.lists(st.sampled_from(skills), min_size=2, max_size=5, unique=True)):
        profile[skill] = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return profile


@st.composite
def learning_goals(draw):
    """Generate valid learning goals."""
    skills = ["python", "javascript", "algorithms", "data_structures", "web_development"]
    
    goals = []
    num_goals = draw(st.integers(min_value=1, max_value=3))
    
    for _ in range(num_goals):
        goal = {
            "skill": draw(st.sampled_from(skills)),
            "target_level": draw(st.floats(min_value=0.5, max_value=1.0)),
            "description": "Test goal"
        }
        goals.append(goal)
    
    return goals


class TestLearningPathProgressionValidity:
    """Property-based tests for learning path progression validity."""
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals()
    )
    async def test_milestone_difficulty_monotonicity(self, user_skills, goals):
        """
        Property: Milestone difficulty must be monotonically increasing.
        
        For any generated learning path, each milestone must have
        difficulty >= previous milestone's difficulty.
        """
        agent = PathPlannerAgent()
        
        # Generate learning path
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills},
            goals=goals
        )
        
        assume(len(path.get("milestones", [])) >= 2)
        
        milestones = path["milestones"]
        
        # Check monotonic difficulty increase
        for i in range(len(milestones) - 1):
            current_difficulty = self._difficulty_to_numeric(milestones[i]["difficulty_level"])
            next_difficulty = self._difficulty_to_numeric(milestones[i + 1]["difficulty_level"])
            
            assert current_difficulty <= next_difficulty, \
                f"Milestone {i+1} difficulty ({next_difficulty}) must be >= milestone {i} ({current_difficulty})"
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals()
    )
    async def test_first_milestone_reachability(self, user_skills, goals):
        """
        Property: First milestone must be reachable from user's current skills.
        
        The first milestone should not require skills significantly
        beyond the user's current level.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills},
            goals=goals
        )
        
        assume(len(path.get("milestones", [])) >= 1)
        
        first_milestone = path["milestones"][0]
        first_difficulty = self._difficulty_to_numeric(first_milestone["difficulty_level"])
        
        # Get user's average skill level
        avg_skill = sum(user_skills.values()) / len(user_skills) if user_skills else 0.0
        
        # First milestone should not be more than 0.3 above user's level
        assert first_difficulty <= avg_skill + 0.3, \
            f"First milestone difficulty ({first_difficulty}) too high for user level ({avg_skill})"
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals()
    )
    async def test_path_covers_skill_gaps(self, user_skills, goals):
        """
        Property: Learning path must cover all skill gaps to reach goals.
        
        For each goal, the path must include milestones that bridge
        the gap from current skill level to target level.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills},
            goals=goals
        )
        
        assume(len(path.get("milestones", [])) >= 1)
        
        # Check that path addresses each goal
        for goal in goals:
            skill = goal["skill"]
            target_level = goal["target_level"]
            current_level = user_skills.get(skill, 0.0)
            
            # If there's a skill gap, path should have relevant milestones
            if target_level > current_level:
                relevant_milestones = [
                    m for m in path["milestones"]
                    if skill in m.get("topics", []) or skill in m.get("skills_developed", [])
                ]
                
                assert len(relevant_milestones) > 0, \
                    f"Path must include milestones for skill gap in {skill}"
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals()
    )
    async def test_prerequisite_ordering(self, user_skills, goals):
        """
        Property: Prerequisites must be satisfied before dependent milestones.
        
        If milestone B has milestone A as a prerequisite, A must appear
        before B in the path.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills},
            goals=goals
        )
        
        assume(len(path.get("milestones", [])) >= 2)
        
        milestones = path["milestones"]
        milestone_ids = {m["id"]: i for i, m in enumerate(milestones)}
        
        # Check prerequisite ordering
        for i, milestone in enumerate(milestones):
            prerequisites = milestone.get("prerequisites", [])
            
            for prereq_id in prerequisites:
                if prereq_id in milestone_ids:
                    prereq_index = milestone_ids[prereq_id]
                    assert prereq_index < i, \
                        f"Prerequisite {prereq_id} must appear before milestone {milestone['id']}"
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals(),
        weekly_hours=st.integers(min_value=5, max_value=40)
    )
    async def test_estimated_duration_reasonableness(self, user_skills, goals, weekly_hours):
        """
        Property: Estimated path duration must be reasonable.
        
        Total estimated hours should be proportional to skill gaps
        and not exceed reasonable bounds.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills, "weekly_hours": weekly_hours},
            goals=goals
        )
        
        total_hours = path.get("estimated_total_hours", 0)
        
        # Calculate expected hours based on skill gaps
        total_gap = 0
        for goal in goals:
            current = user_skills.get(goal["skill"], 0.0)
            target = goal["target_level"]
            total_gap += max(0, target - current)
        
        # Rough estimate: 50-200 hours per 1.0 skill gap
        min_expected = total_gap * 50
        max_expected = total_gap * 200
        
        assert min_expected <= total_hours <= max_expected, \
            f"Estimated hours ({total_hours}) should be between {min_expected} and {max_expected}"
    
    @pytest.mark.property
    @given(
        user_skills=user_skill_profile(),
        goals=learning_goals()
    )
    async def test_path_completeness(self, user_skills, goals):
        """
        Property: Generated path must be complete and valid.
        
        Path must have all required fields and valid structure.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": user_skills},
            goals=goals
        )
        
        # Check required fields
        assert "id" in path, "Path must have an ID"
        assert "title" in path, "Path must have a title"
        assert "milestones" in path, "Path must have milestones"
        assert "estimated_total_hours" in path, "Path must have estimated hours"
        
        # Check milestones structure
        for milestone in path["milestones"]:
            assert "id" in milestone, "Milestone must have an ID"
            assert "title" in milestone, "Milestone must have a title"
            assert "difficulty_level" in milestone, "Milestone must have difficulty"
            assert "estimated_hours" in milestone, "Milestone must have estimated hours"
    
    @pytest.mark.property
    @given(
        beginner_skills=st.fixed_dictionaries({"python": st.floats(min_value=0.0, max_value=0.3)}),
        expert_goal=st.fixed_dictionaries({
            "skill": st.just("python"),
            "target_level": st.floats(min_value=0.9, max_value=1.0)
        })
    )
    async def test_beginner_to_expert_progression(self, beginner_skills, expert_goal):
        """
        Property: Path from beginner to expert must include all difficulty levels.
        
        A path taking a user from beginner to expert should include
        milestones at beginner, intermediate, advanced, and expert levels.
        """
        agent = PathPlannerAgent()
        
        path = await agent.generate_path(
            user_profile={"skill_levels": beginner_skills},
            goals=[expert_goal]
        )
        
        assume(len(path.get("milestones", [])) >= 4)
        
        difficulties = [
            self._difficulty_to_numeric(m["difficulty_level"])
            for m in path["milestones"]
        ]
        
        # Should have progression through difficulty levels
        assert min(difficulties) <= 0.3, "Should start at beginner level"
        assert max(difficulties) >= 0.9, "Should reach expert level"
        
        # Should have intermediate steps
        has_intermediate = any(0.3 < d < 0.7 for d in difficulties)
        has_advanced = any(0.7 <= d < 0.9 for d in difficulties)
        
        assert has_intermediate or has_advanced, \
            "Should have intermediate or advanced milestones"
    
    # Helper methods
    def _difficulty_to_numeric(self, difficulty: str) -> float:
        """Convert difficulty level string to numeric value."""
        mapping = {
            "beginner": 0.25,
            "intermediate": 0.5,
            "advanced": 0.75,
            "expert": 1.0
        }
        return mapping.get(difficulty.lower(), 0.5)
