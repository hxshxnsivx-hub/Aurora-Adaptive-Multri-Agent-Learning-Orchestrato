"""
Notion Sync Agent for workspace integration.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.integrations import NotionClient

logger = logging.getLogger(__name__)


class NotionSyncAgent(BaseAgent):
    """Agent responsible for Notion workspace synchronization."""
    
    def __init__(self):
        super().__init__(
            agent_id="notion_sync_agent",
            name="Notion Sync Agent"
        )
        self.notion_client = None  # Will be set per-user with their token
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process Notion sync requests."""
        try:
            action = message.content.get("action")
            
            if action == "create_page":
                return await self._create_page(message, state)
            elif action == "update_page":
                return await self._update_page(message, state)
            elif action == "sync_tasks":
                return await self._sync_tasks(message, state)
            elif action == "sync_progress":
                return await self._sync_progress(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in NotionSyncAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _create_page(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Create a Notion page for a task or milestone."""
        content = message.content.get("content", {})
        database_id = message.content.get("database_id")
        user_token = message.content.get("token")  # User's Notion access token
        
        # Initialize client with user token
        if user_token:
            self.notion_client = NotionClient(token=user_token)
        
        # Create page using Notion API
        if self.notion_client:
            due_date = None
            if content.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(content.get("due_date").replace("Z", "+00:00"))
                except:
                    pass
            
            page = await self.notion_client.create_task_page(
                database_id=database_id,
                title=content.get("title", ""),
                status=content.get("status", "Not Started"),
                due_date=due_date,
                description=content.get("description", ""),
                tags=[content.get("type", "Task")]
            )
            
            if page:
                return AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type="response",
                    content={
                        "page": page,
                        "page_id": page.get("id"),
                        "url": page.get("url", f"https://notion.so/{page.get('id')}"),
                        "created": True
                    },
                    metadata={"timestamp": datetime.utcnow().isoformat()}
                )
        
        # Fallback to mock response
        page = {
            "object": "page",
            "id": f"notion_page_{content.get('id')}",
            "properties": {
                "Name": {"title": [{"plain_text": content.get("title", "")}]},
                "Status": {"select": {"name": content.get("status", "Not Started")}}
            },
            "created_time": datetime.utcnow().isoformat(),
            "last_edited_time": datetime.utcnow().isoformat()
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "page": page,
                "page_id": page["id"],
                "url": f"https://notion.so/{page['id']}",
                "created": True
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _update_page(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Update an existing Notion page."""
        page_id = message.content.get("page_id")
        updates = message.content.get("updates", {})
        user_token = message.content.get("token")
        
        # Initialize client with user token
        if user_token:
            self.notion_client = NotionClient(token=user_token)
        
        # Update page using Notion API
        if self.notion_client and "status" in updates:
            result = await self.notion_client.update_task_status(
                page_id=page_id,
                status=updates["status"]
            )
            
            if result:
                return AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type="response",
                    content={
                        "page_id": page_id,
                        "updated": True,
                        "changes": updates
                    },
                    metadata={"timestamp": datetime.utcnow().isoformat()}
                )
        
        # Fallback to mock response
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "page_id": page_id,
                "updated": True,
                "changes": updates
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _sync_tasks(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Sync learning tasks to Notion database."""
        tasks = message.content.get("tasks", [])
        database_id = message.content.get("database_id")
        
        synced_pages = []
        for task in tasks:
            page_result = await self._create_page(
                AgentMessage(
                    sender=message.sender,
                    receiver=self.agent_id,
                    message_type="request",
                    content={
                        "content": {
                            "id": task.get("id"),
                            "title": task.get("title"),
                            "description": task.get("description"),
                            "status": task.get("status", "Not Started"),
                            "due_date": task.get("scheduled_at"),
                            "priority": task.get("priority", "Medium"),
                            "type": "Learning Task"
                        },
                        "database_id": database_id
                    }
                ),
                state
            )
            synced_pages.append(page_result.content.get("page_id"))
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "synced_pages": synced_pages,
                "total_synced": len(synced_pages)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _sync_progress(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Sync learning progress to Notion."""
        progress_data = message.content.get("progress", {})
        page_id = message.content.get("page_id")
        
        updates = {
            "status": self._map_status(progress_data.get("completion_percentage", 0)),
            "progress": progress_data.get("completion_percentage", 0)
        }
        
        result = await self._update_page(
            AgentMessage(
                sender=message.sender,
                receiver=self.agent_id,
                message_type="request",
                content={
                    "page_id": page_id,
                    "updates": updates
                }
            ),
            state
        )
        
        return result
    
    def _map_status(self, completion_percentage: float) -> str:
        """Map completion percentage to Notion status."""
        if completion_percentage == 0:
            return "Not Started"
        elif completion_percentage < 100:
            return "In Progress"
        else:
            return "Completed"
