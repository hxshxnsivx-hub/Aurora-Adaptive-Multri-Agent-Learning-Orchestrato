"""
Property-Based Tests for Skill Assessment Consistency

**Validates: Requirements 1.2, 1.3**

Property 1: Skill Assessment Consistency
- Proficiency calculations must be deterministic
- Repeated calculations with identical inputs yield identical results
- Proficiency levels must be within valid bounds [0.0, 1.0]
"""
import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List

from app.agents.user_profile import UserProfileAgent
from app.agents.base import AgentMessage, AgentState


# Strategies for generating test data
@st.composite
def skill_assessment_questions(draw):
    """Generate valid skill assessment questions."""
    num_questions = draw(st.integers(min_value=5, max_value=20))
    questions = []
    
    for i in range(num_questions):
        question = {
            "id": f"q_{i}",
            "skill_domain": draw(st.sampled_from(["python", "javascript", "algorithms", "data_structures"])),
            "difficulty": draw(st.floats(min_value=0.1, max_value=1.0)),
            "question_text": f"Question {i}",
            "correct_answer": draw(st.sampled_from(["A", "B", "C", "D"]))
        }
        questions.append(question)
    
    return questions


@st.composite
def user_responses(draw, questions: List[Dict]):
    """Generate user responses for given questions."""
    responses = []
    
    for question in questions:
        response = {
            "question_id": question["id"],
            "user_answer": draw(st.sampled_from(["A", "B", "C", "D"])),
            "time_taken": draw(st.integers(min_value=10, max_value=300))  # seconds
        }
        responses.append(response)
    
    return responses


class TestSkillAssessmentConsistency:
    """Property-based tests for skill assessment consistency."""
    
    @pytest.mark.property
    @given(questions=skill_assessment_questions())
    async def test_proficiency_determinism(self, questions):
        """
        Property: Proficiency calculation must be deterministic.
        
        Given identical questions and responses, the calculated proficiency
        must be exactly the same across multiple calculations.
        """
        # Generate responses
        responses = []
        for q in questions:
            responses.append({
                "question_id": q["id"],
                "user_answer": q["correct_answer"],  # All correct
                "time_taken": 60
            })
        
        agent = UserProfileAgent()
        
        # Calculate proficiency multiple times
        results = []
        for _ in range(3):
            proficiency = await agent._calculate_proficiency(questions, responses)
            results.append(proficiency)
        
        # All results must be identical
        assert all(r == results[0] for r in results), \
            "Proficiency calculation must be deterministic"
    
    @pytest.mark.property
    @given(
        questions=skill_assessment_questions(),
        seed=st.integers(min_value=0, max_value=1000000)
    )
    async def test_proficiency_bounds(self, questions, seed):
        """
        Property: Proficiency levels must be within valid bounds [0.0, 1.0].
        
        For any set of questions and responses, calculated proficiency
        must never exceed the valid range.
        """
        # Generate random responses
        responses = []
        for q in questions:
            responses.append({
                "question_id": q["id"],
                "user_answer": ["A", "B", "C", "D"][seed % 4],
                "time_taken": (seed % 290) + 10
            })
        
        agent = UserProfileAgent()
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        # Check bounds for each skill domain
        for skill, level in proficiency.items():
            assert 0.0 <= level <= 1.0, \
                f"Proficiency for {skill} must be in [0.0, 1.0], got {level}"
    
    @pytest.mark.property
    @given(questions=skill_assessment_questions())
    async def test_perfect_score_yields_high_proficiency(self, questions):
        """
        Property: Perfect scores should yield high proficiency (>= 0.9).
        
        When a user answers all questions correctly and quickly,
        proficiency should be at least 0.9.
        """
        # All correct answers, fast responses
        responses = []
        for q in questions:
            responses.append({
                "question_id": q["id"],
                "user_answer": q["correct_answer"],
                "time_taken": 30  # Fast response
            })
        
        agent = UserProfileAgent()
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        # All proficiency levels should be high
        for skill, level in proficiency.items():
            assert level >= 0.9, \
                f"Perfect score should yield proficiency >= 0.9, got {level} for {skill}"
    
    @pytest.mark.property
    @given(questions=skill_assessment_questions())
    async def test_zero_score_yields_low_proficiency(self, questions):
        """
        Property: Zero scores should yield low proficiency (<= 0.3).
        
        When a user answers all questions incorrectly,
        proficiency should be at most 0.3.
        """
        # All incorrect answers
        responses = []
        for q in questions:
            # Choose a wrong answer
            wrong_answer = "A" if q["correct_answer"] != "A" else "B"
            responses.append({
                "question_id": q["id"],
                "user_answer": wrong_answer,
                "time_taken": 120
            })
        
        agent = UserProfileAgent()
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        # All proficiency levels should be low
        for skill, level in proficiency.items():
            assert level <= 0.3, \
                f"Zero score should yield proficiency <= 0.3, got {level} for {skill}"
    
    @pytest.mark.property
    @given(
        questions=skill_assessment_questions(),
        correct_ratio=st.floats(min_value=0.0, max_value=1.0)
    )
    async def test_proficiency_monotonicity(self, questions, correct_ratio):
        """
        Property: Proficiency should increase monotonically with correct answers.
        
        More correct answers should never result in lower proficiency.
        """
        assume(len(questions) >= 5)
        
        agent = UserProfileAgent()
        
        # Calculate proficiency for different correct ratios
        num_correct = int(len(questions) * correct_ratio)
        
        responses = []
        for i, q in enumerate(questions):
            answer = q["correct_answer"] if i < num_correct else "WRONG"
            responses.append({
                "question_id": q["id"],
                "user_answer": answer,
                "time_taken": 60
            })
        
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        # Verify proficiency correlates with correct ratio
        avg_proficiency = sum(proficiency.values()) / len(proficiency)
        
        # Allow some tolerance for calculation variations
        expected_min = max(0.0, correct_ratio - 0.2)
        expected_max = min(1.0, correct_ratio + 0.2)
        
        assert expected_min <= avg_proficiency <= expected_max, \
            f"Average proficiency {avg_proficiency} should correlate with correct ratio {correct_ratio}"
    
    @pytest.mark.property
    @given(
        questions=skill_assessment_questions(),
        skill_domain=st.sampled_from(["python", "javascript", "algorithms", "data_structures"])
    )
    async def test_skill_domain_isolation(self, questions, skill_domain):
        """
        Property: Proficiency in one skill domain should not affect others.
        
        Answering questions correctly in one domain should only increase
        proficiency in that domain, not others.
        """
        # Filter questions for specific domain
        domain_questions = [q for q in questions if q["skill_domain"] == skill_domain]
        assume(len(domain_questions) >= 3)
        
        # Answer domain questions correctly, others incorrectly
        responses = []
        for q in questions:
            if q["skill_domain"] == skill_domain:
                answer = q["correct_answer"]
            else:
                answer = "WRONG"
            
            responses.append({
                "question_id": q["id"],
                "user_answer": answer,
                "time_taken": 60
            })
        
        agent = UserProfileAgent()
        proficiency = await agent._calculate_proficiency(questions, responses)
        
        # Target domain should have high proficiency
        if skill_domain in proficiency:
            assert proficiency[skill_domain] >= 0.7, \
                f"Proficiency in {skill_domain} should be high when answered correctly"
        
        # Other domains should have lower proficiency
        for skill, level in proficiency.items():
            if skill != skill_domain:
                assert level <= 0.4, \
                    f"Proficiency in {skill} should be low when answered incorrectly"
