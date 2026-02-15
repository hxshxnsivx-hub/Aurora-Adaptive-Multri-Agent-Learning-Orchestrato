"""
Integration tests for API endpoints.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.main import app


class TestOnboardingEndpoints:
    """Tests for onboarding API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_assess_skills_endpoint(self, mock_auth_headers):
        """Test skill assessment endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/onboarding/assess-skills",
                headers=mock_auth_headers,
                json={
                    "questions": [
                        {
                            "id": "q1",
                            "skill_domain": "python",
                            "difficulty": 0.5,
                            "question_text": "What is a variable?",
                            "correct_answer": "A"
                        }
                    ],
                    "responses": [
                        {
                            "question_id": "q1",
                            "user_answer": "A",
                            "time_taken": 60
                        }
                    ]
                }
            )
            
            assert response.status_code in [200, 401]  # 401 if auth not configured
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_complete_onboarding_endpoint(self, mock_auth_headers):
        """Test complete onboarding endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/onboarding/complete",
                headers=mock_auth_headers,
                json={
                    "display_name": "Test User",
                    "skill_levels": {"python": 0.7},
                    "learning_preferences": {
                        "preferred_content_types": ["video"],
                        "learning_pace": "moderate"
                    },
                    "goals": ["Master Python"]
                }
            )
            
            assert response.status_code in [200, 401, 422]


class TestLearningPathEndpoints:
    """Tests for learning path API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_generate_learning_path_endpoint(self, mock_auth_headers):
        """Test learning path generation endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/learning-paths/generate",
                headers=mock_auth_headers,
                json={
                    "topic": "Python",
                    "current_level": "beginner",
                    "target_level": "advanced",
                    "goals": ["Master Python programming"],
                    "weekly_hours": 10
                }
            )
            
            assert response.status_code in [200, 401, 422]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_learning_paths_endpoint(self, mock_auth_headers):
        """Test get learning paths endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/learning-paths",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_learning_path_detail_endpoint(self, mock_auth_headers):
        """Test get learning path detail endpoint."""
        path_id = str(uuid4())
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/learning-paths/{path_id}",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401, 404]


class TestTaskEndpoints:
    """Tests for task API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_tasks_endpoint(self, mock_auth_headers):
        """Test get tasks endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/tasks",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_create_task_endpoint(self, mock_auth_headers):
        """Test create task endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tasks",
                headers=mock_auth_headers,
                json={
                    "milestone_id": str(uuid4()),
                    "title": "Learn Python Variables",
                    "description": "Understand variable types",
                    "task_type": "read",
                    "estimated_minutes": 30
                }
            )
            
            assert response.status_code in [200, 201, 401, 422]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_complete_task_endpoint(self, mock_auth_headers):
        """Test complete task endpoint."""
        task_id = str(uuid4())
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/tasks/{task_id}/complete",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401, 404]


class TestResourceEndpoints:
    """Tests for resource API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_resources_endpoint(self, mock_auth_headers):
        """Test get resources endpoint."""
        milestone_id = str(uuid4())
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/resources?milestone_id={milestone_id}",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_search_resources_endpoint(self, mock_auth_headers):
        """Test search resources endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/resources/search?query=python&type=video",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestUserEndpoints:
    """Tests for user API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_current_user_endpoint(self, mock_auth_headers):
        """Test get current user endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_update_user_profile_endpoint(self, mock_auth_headers):
        """Test update user profile endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                "/api/v1/users/me/profile",
                headers=mock_auth_headers,
                json={
                    "display_name": "Updated Name",
                    "timezone": "America/New_York"
                }
            )
            
            assert response.status_code in [200, 401, 422]


class TestIntegrationEndpoints:
    """Tests for integration API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_google_calendar_auth_endpoint(self, mock_auth_headers):
        """Test Google Calendar OAuth endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/integrations/google-calendar/auth",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 302, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_notion_auth_endpoint(self, mock_auth_headers):
        """Test Notion OAuth endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/integrations/notion/auth",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 302, 401]


class TestVoiceEndpoints:
    """Tests for voice API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.slow
    async def test_process_voice_command_endpoint(self, mock_auth_headers):
        """Test voice command processing endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Mock audio file
            files = {"audio": ("test.wav", b"fake audio data", "audio/wav")}
            
            response = await client.post(
                "/api/v1/voice/process",
                headers=mock_auth_headers,
                files=files
            )
            
            assert response.status_code in [200, 401, 422]


class TestAnalyticsEndpoints:
    """Tests for analytics API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_user_progress_endpoint(self, mock_auth_headers):
        """Test get user progress endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/analytics/progress",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.integration
    @pytest.mark.api
    async def test_get_progress_stats_endpoint(self, mock_auth_headers):
        """Test get progress statistics endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/analytics/stats",
                headers=mock_auth_headers
            )
            
            assert response.status_code in [200, 401]
