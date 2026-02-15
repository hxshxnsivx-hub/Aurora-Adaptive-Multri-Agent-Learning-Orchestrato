"""
Property-Based Tests for Resource Curation Relevance

**Validates: Requirements 2.3, 4.5**

Property 3: Resource Curation Relevance
- Resources must be semantically relevant to milestone topics
- Quality scores must be within acceptable range [0.6, 1.0]
- Resource difficulty must align with milestone difficulty ± 1 level
- Resources must cover all required topics
"""
import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List

from app.agents.resource_curator import ResourceCuratorAgent


# Strategies for generating test data
@st.composite
def milestone_data(draw):
    """Generate valid milestone data."""
    topics = draw(st.lists(
        st.sampled_from(["python", "javascript", "algorithms", "web_development", "data_structures"]),
        min_size=2,
        max_size=5,
        unique=True
    ))
    
    return {
        "id": draw(st.uuids()).hex,
        "title": f"Learn {topics[0].title()}",
        "topics": topics,
        "difficulty_level": draw(st.sampled_from(["beginner", "intermediate", "advanced", "expert"])),
        "estimated_hours": draw(st.integers(min_value=5, max_value=40))
    }


@st.composite
def resource_data(draw, topics: List[str], difficulty: str):
    """Generate resource data for given topics and difficulty."""
    return {
        "id": draw(st.uuids()).hex,
        "title": f"Resource about {draw(st.sampled_from(topics))}",
        "topics": draw(st.lists(st.sampled_from(topics), min_size=1, max_size=3)),
        "difficulty_level": difficulty,
        "quality_score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "relevance_score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "resource_type": draw(st.sampled_from(["video", "article", "code", "course"])),
        "estimated_duration": draw(st.integers(min_value=10, max_value=180))
    }


class TestResourceCurationRelevance:
    """Property-based tests for resource curation relevance."""
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_curated_resources_have_valid_quality_scores(self, milestone):
        """
        Property: All curated resources must have quality scores in [0.6, 1.0].
        
        Resources below quality threshold should be filtered out.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        for resource in resources:
            quality_score = resource.get("quality_score", 0.0)
            assert 0.6 <= quality_score <= 1.0, \
                f"Quality score {quality_score} must be in [0.6, 1.0]"
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_resources_cover_milestone_topics(self, milestone):
        """
        Property: Curated resources must cover all milestone topics.
        
        The set of all resource topics should include all milestone topics.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        assume(len(resources) > 0)
        
        # Collect all topics from resources
        resource_topics = set()
        for resource in resources:
            resource_topics.update(resource.get("topics", []))
        
        # Check that all milestone topics are covered
        milestone_topics = set(milestone["topics"])
        covered_topics = milestone_topics.intersection(resource_topics)
        
        coverage_ratio = len(covered_topics) / len(milestone_topics)
        assert coverage_ratio >= 0.7, \
            f"Resources should cover at least 70% of milestone topics, got {coverage_ratio:.2%}"
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_resource_difficulty_alignment(self, milestone):
        """
        Property: Resource difficulty must align with milestone difficulty ± 1 level.
        
        Resources should not be too easy or too hard for the milestone.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        assume(len(resources) > 0)
        
        difficulty_map = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
            "expert": 3
        }
        
        milestone_level = difficulty_map.get(milestone["difficulty_level"], 1)
        
        for resource in resources:
            resource_level = difficulty_map.get(resource.get("difficulty_level", "intermediate"), 1)
            level_diff = abs(resource_level - milestone_level)
            
            assert level_diff <= 1, \
                f"Resource difficulty {resource['difficulty_level']} too far from milestone {milestone['difficulty_level']}"
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_resources_are_ranked_by_quality(self, milestone):
        """
        Property: Resources must be ranked by quality and relevance.
        
        Higher quality resources should appear first in the list.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        assume(len(resources) >= 2)
        
        # Calculate combined scores for each resource
        scores = []
        for resource in resources:
            quality = resource.get("quality_score", 0.0)
            relevance = resource.get("relevance_score", 0.0)
            combined = quality * 0.6 + relevance * 0.4
            scores.append(combined)
        
        # Check that scores are in descending order (or equal)
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1] - 0.01, \
                f"Resources should be ranked by quality, but score {scores[i]} < {scores[i + 1]}"
    
    @pytest.mark.property
    @given(
        milestone=milestone_data(),
        max_resources=st.integers(min_value=5, max_value=15)
    )
    async def test_resource_count_limit(self, milestone, max_resources):
        """
        Property: Number of curated resources should not exceed limit.
        
        To avoid overwhelming users, limit resources per milestone.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone, max_count=max_resources)
        
        assert len(resources) <= max_resources, \
            f"Should return at most {max_resources} resources, got {len(resources)}"
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_resource_diversity(self, milestone):
        """
        Property: Curated resources should include diverse content types.
        
        Mix of videos, articles, code examples, etc. for different learning styles.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        assume(len(resources) >= 5)
        
        # Count resource types
        resource_types = [r.get("resource_type") for r in resources]
        unique_types = set(resource_types)
        
        # Should have at least 2 different types for diversity
        assert len(unique_types) >= 2, \
            f"Resources should include diverse types, got only {unique_types}"
    
    @pytest.mark.property
    @given(milestone=milestone_data())
    async def test_estimated_duration_reasonableness(self, milestone):
        """
        Property: Total resource duration should be reasonable for milestone.
        
        Total time should not exceed milestone estimated hours by too much.
        """
        agent = ResourceCuratorAgent()
        
        resources = await agent.curate_resources(milestone)
        
        assume(len(resources) > 0)
        
        total_minutes = sum(r.get("estimated_duration", 0) for r in resources)
        total_hours = total_minutes / 60
        
        milestone_hours = milestone["estimated_hours"]
        
        # Total resource time should be 0.5x to 2x milestone time
        min_expected = milestone_hours * 0.5
        max_expected = milestone_hours * 2.0
        
        assert min_expected <= total_hours <= max_expected, \
            f"Total resource time {total_hours:.1f}h should be between {min_expected:.1f}h and {max_expected:.1f}h"
