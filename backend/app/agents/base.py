"""
Base agent class and common utilities for the multi-agent system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Standard message format for agent communication."""
    id: str = None
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = None
    correlation_id: Optional[str] = None
    
    def __init__(self, **data):
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        if not data.get('timestamp'):
            data['timestamp'] = datetime.now()
        super().__init__(**data)


class AgentState(BaseModel):
    """Base state model for agents."""
    agent_id: str
    status: str = "idle"  # idle, processing, error, completed
    current_task: Optional[str] = None
    context: Dict[str, Any] = {}
    last_updated: datetime = None
    
    def __init__(self, **data):
        if not data.get('last_updated'):
            data['last_updated'] = datetime.now()
        super().__init__(**data)


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.state = AgentState(agent_id=agent_id)
        self.message_history: List[AgentMessage] = []
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message and optionally return a response."""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent."""
        pass
    
    def update_state(self, status: str, task: Optional[str] = None, context: Dict[str, Any] = None):
        """Update agent state."""
        self.state.status = status
        if task:
            self.state.current_task = task
        if context:
            self.state.context.update(context)
        self.state.last_updated = datetime.now()
        
        self.logger.info(f"Agent {self.name} state updated: {status}")
    
    def add_message_to_history(self, message: AgentMessage):
        """Add message to agent's history."""
        self.message_history.append(message)
        # Keep only last 100 messages to prevent memory issues
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]
    
    async def send_message(self, recipient: str, message_type: str, content: Dict[str, Any]) -> AgentMessage:
        """Create and send a message to another agent."""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            content=content
        )
        
        self.add_message_to_history(message)
        self.logger.info(f"Sent message to {recipient}: {message_type}")
        
        return message
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides."""
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "last_updated": self.state.last_updated,
            "capabilities": self.get_capabilities()
        }