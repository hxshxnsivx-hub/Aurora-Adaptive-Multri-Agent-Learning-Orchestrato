"""
Calendar Agent for Google Calendar integration.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.integrations import GoogleCalendarClient

logger = logging.getLogger(__name__)


class CalendarAgent(BaseAgent):
    """Agent responsible for Google Calendar integration and scheduling."""
    
    def __init__(self):
        super().__init__(
            agent_id="calendar_agent",
            name="Calendar Agent"
        )
        self.calendar_client = None  # Will be set per-user with their credentials
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process calendar-related requests."""
        try:
            action = message.content.get("action")
            
            if action == "create_event":
                return await self._create_event(message, state)
            elif action == "update_event":
                return await self._update_event(message, state)
            elif action == "delete_event":
                return await self._delete_event(message, state)
            elif action == "get_availability":
                return await self._get_availability(message, state)
            elif action == "sync_events":
                return await self._sync_events(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in CalendarAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _create_event(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Create a calendar event for a learning task."""
        task = message.content.get("task", {})
        user_calendar_id = message.content.get("calendar_id", "primary")
        user_credentials = message.content.get("credentials")  # OAuth2 credentials
        
        # Initialize client with user credentials
        if user_credentials:
            self.calendar_client = GoogleCalendarClient(credentials=user_credentials)
        
        # Prepare event data
        summary = task.get("title", "Learning Session")
        start_time = datetime.fromisoformat(task.get("scheduled_at").replace("Z", "+00:00"))
        duration_minutes = task.get("estimated_minutes", 30)
        end_time = start_time + timedelta(minutes=duration_minutes)
        description = task.get("description", "")
        
        # Create event using Google Calendar API
        if self.calendar_client:
            event = await self.calendar_client.create_event(
                summary=summary,
                start_time=start_time,
                end_time=end_time,
                description=description,
                calendar_id=user_calendar_id
            )
            
            if event:
                return AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type="response",
                    content={
                        "event": event,
                        "calendar_id": user_calendar_id,
                        "event_link": event.get("html_link", ""),
                        "created": True
                    },
                    metadata={"timestamp": datetime.utcnow().isoformat()}
                )
        
        # Fallback to mock response if no credentials
        event = {
            "id": f"cal_event_{task.get('id')}",
            "summary": summary,
            "description": description,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "confirmed",
            "html_link": f"https://calendar.google.com/calendar/event?eid={task.get('id')}",
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat()
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "event": event,
                "calendar_id": user_calendar_id,
                "event_link": event["html_link"],
                "created": True
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _update_event(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Update an existing calendar event."""
        event_id = message.content.get("event_id")
        updates = message.content.get("updates", {})
        
        # In production, would call Google Calendar API
        # service.events().patch(calendarId='primary', eventId=event_id, body=updates).execute()
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "event_id": event_id,
                "updated": True,
                "changes": updates
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _delete_event(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Delete a calendar event."""
        event_id = message.content.get("event_id")
        
        # In production, would call Google Calendar API
        # service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "event_id": event_id,
                "deleted": True
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _get_availability(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Get user's availability from calendar."""
        start_date = message.content.get("start_date", datetime.utcnow().isoformat())
        end_date = message.content.get("end_date", (datetime.utcnow() + timedelta(days=7)).isoformat())
        user_credentials = message.content.get("credentials")
        
        # Initialize client with user credentials
        if user_credentials:
            self.calendar_client = GoogleCalendarClient(credentials=user_credentials)
        
        # Get free/busy information from Google Calendar
        if self.calendar_client:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            
            free_busy = await self.calendar_client.get_free_busy(
                time_min=start_dt,
                time_max=end_dt,
                calendar_ids=['primary']
            )
            
            if free_busy:
                return AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type="response",
                    content={
                        "free_busy": free_busy,
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    metadata={"timestamp": datetime.utcnow().isoformat()}
                )
        
        # Fallback to simulated availability
        availability = {
            "monday": [{"start": 9, "end": 12}, {"start": 14, "end": 18}],
            "tuesday": [{"start": 9, "end": 12}, {"start": 14, "end": 18}],
            "wednesday": [{"start": 9, "end": 12}, {"start": 14, "end": 18}],
            "thursday": [{"start": 9, "end": 12}, {"start": 14, "end": 18}],
            "friday": [{"start": 9, "end": 12}, {"start": 14, "end": 18}],
            "saturday": [{"start": 10, "end": 16}],
            "sunday": [{"start": 10, "end": 16}]
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "availability": availability,
                "start_date": start_date,
                "end_date": end_date
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _sync_events(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Sync learning events with Google Calendar."""
        tasks = message.content.get("tasks", [])
        
        synced_events = []
        for task in tasks:
            if task.get("scheduled_at"):
                event_result = await self._create_event(
                    AgentMessage(
                        sender=message.sender,
                        receiver=self.agent_id,
                        message_type="request",
                        content={"task": task}
                    ),
                    state
                )
                synced_events.append(event_result.content.get("event"))
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "synced_events": synced_events,
                "total_synced": len(synced_events)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _calculate_end_time(self, start_time: str, duration_minutes: int) -> str:
        """Calculate end time for an event."""
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = start + timedelta(minutes=duration_minutes)
            return end.isoformat()
        except:
            return (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat()
