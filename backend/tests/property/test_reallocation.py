"""
Property-Based Tests for Reallocation Coherence

**Validates: Requirements 3.1, 3.4**

Property 5: Reallocation Coherence
- Goal alignment must be preserved after reallocation
- Learning progression must remain valid
- Total estimated time variance must be within ±20%
- All prerequisite relationships must be maintained
"""
import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List

from app.agents.reallocation import ReallocationAgent


# Strategies for generating test data
@st.composite
def learning_path_data(draw):
    """Generate valid learning path data."""
    num_milestones = draw(st.integers(min_value=3, max_value=10))
    
    milestones = []
    for i in range(num_milestones):
        milestone = {
            "id": f"milestone_{i}",
            "title": f"Milestone {i}",
            "difficulty_level": draw(st.sampled_from(["beginner", "intermediate", "advanced", "expert"])),
            "estimated_hours": draw(st.integers(min_value=5, max_value=30)),
            "order_index": i,
            "prerequisites": []
        }
        
        # Add prerequisites to earlier milestones
        if i > 0 and draw(st.booleans()):
            prereq_index = draw(st.integers(min_value=0, max_value=i-1))
            milestone["prerequisites"] = [f"milestone_{prereq_index}"]
        
        milestones.append(milestone)
    
    goals = draw(st.lists(
        st.text(min_size=10, max_size=50),
        min_size=1,
        max_size=3
    ))
    
    total_hours = sum(m["estimated_hours"] for m in milestones)
    
    return {
        "id": "path_1",
        "title": "Learning Path",
        "goals": goals,
        "milestones": milestones,
        "estimated_total_hours": total_hours
    }


@st.composite
def reallocation_feedback(draw):
    """Generate reallocation feedback."""
    return {
        "reason": draw(st.sampled_from(["too_easy", "too_hard", "behind_schedule", "user_feedback"])),
        "current_milestone_id": draw(st.text(min_size=5, max_size=20)),
        "difficulty_adjustment": draw(st.sampled_from(["easier", "harder", "same"])),
        "time_adjustment": draw(st.floats(min_value=0.8, max_value=1.2))
    }


class TestReallocationCoherence:
    """Property-based tests for reallocation coherence."""
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_goals_preserved_after_reallocation(self, original_path, feedback):
        """
        Property: Goals must be preserved after reallocation.
        
        Reallocation should not change the learning objectives.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        assert new_path["goals"] == original_path["goals"], \
            "Goals must be preserved after reallocation"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_progression_validity_maintained(self, original_path, feedback):
        """
        Property: Learning progression must remain valid after reallocation.
        
        Milestone difficulty should still be monotonically increasing.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        milestones = new_path["milestones"]
        assume(len(milestones) >= 2)
        
        difficulty_map = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
            "expert": 3
        }
        
        for i in range(len(milestones) - 1):
            current_diff = difficulty_map.get(milestones[i]["difficulty_level"], 1)
            next_diff = difficulty_map.get(milestones[i + 1]["difficulty_level"], 1)
            
            assert current_diff <= next_diff, \
                f"Progression invalid: milestone {i} difficulty {current_diff} > milestone {i+1} difficulty {next_diff}"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_time_variance_within_bounds(self, original_path, feedback):
        """
        Property: Total estimated time variance must be within ±20%.
        
        Reallocation should not drastically change time commitment.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        original_hours = original_path["estimated_total_hours"]
        new_hours = new_path["estimated_total_hours"]
        
        variance = abs(new_hours - original_hours) / original_hours if original_hours > 0 else 0
        
        assert variance <= 0.20, \
            f"Time variance {variance:.2%} exceeds 20% limit"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_prerequisites_maintained(self, original_path, feedback):
        """
        Property: Prerequisite relationships must be maintained or updated.
        
        Dependencies should remain valid after reallocation.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        milestones = new_path["milestones"]
        milestone_ids = {m["id"] for m in milestones}
        
        for milestone in milestones:
            for prereq_id in milestone.get("prerequisites", []):
                assert prereq_id in milestone_ids, \
                    f"Prerequisite {prereq_id} not found in reallocated path"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_milestone_count_reasonable(self, original_path, feedback):
        """
        Property: Number of milestones should remain reasonable.
        
        Reallocation should not drastically change path structure.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        original_count = len(original_path["milestones"])
        new_count = len(new_path["milestones"])
        
        # Allow ±50% change in milestone count
        min_count = int(original_count * 0.5)
        max_count = int(original_count * 1.5)
        
        assert min_count <= new_count <= max_count, \
            f"Milestone count {new_count} outside reasonable range [{min_count}, {max_count}]"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_difficulty_adjustment_applied(self, original_path, feedback):
        """
        Property: Difficulty adjustment should be reflected in new path.
        
        If feedback requests easier/harder, path should adjust accordingly.
        """
        agent = ReallocationAgent()
        
        new_path = await agent.reallocate_path(original_path, feedback)
        
        difficulty_map = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
            "expert": 3
        }
        
        original_avg = sum(
            difficulty_map.get(m["difficulty_level"], 1)
            for m in original_path["milestones"]
        ) / len(original_path["milestones"])
        
        new_avg = sum(
            difficulty_map.get(m["difficulty_level"], 1)
            for m in new_path["milestones"]
        ) / len(new_path["milestones"])
        
        adjustment = feedback["difficulty_adjustment"]
        
        if adjustment == "easier":
            assert new_avg <= original_avg + 0.5, \
                "Path should be easier or same difficulty"
        elif adjustment == "harder":
            assert new_avg >= original_avg - 0.5, \
                "Path should be harder or same difficulty"
    
    @pytest.mark.property
    @given(
        original_path=learning_path_data(),
        feedback=reallocation_feedback()
    )
    async def test_reallocation_idempotency(self, original_path, feedback):
        """
        Property: Reallocating with same feedback should be idempotent.
        
        Applying same reallocation twice should not change result.
        """
        agent = ReallocationAgent()
        
        new_path1 = await agent.reallocate_path(original_path, feedback)
        new_path2 = await agent.reallocate_path(original_path, feedback)
        
        # Key properties should be identical
        assert new_path1["goals"] == new_path2["goals"]
        assert len(new_path1["milestones"]) == len(new_path2["milestones"])
        assert abs(new_path1["estimated_total_hours"] - new_path2["estimated_total_hours"]) < 1
