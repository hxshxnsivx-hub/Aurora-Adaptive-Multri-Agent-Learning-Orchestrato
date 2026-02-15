"""
Central Orchestrator Agent - coordinates all agent interactions.
"""

from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent, AgentMessage
import asyncio
import logging

logger = logging.getLogger(__name__)


class CentralOrchestrator(BaseAgent):
    """Central orchestrator that coordinates all agent interactions."""
    
    def __init__(self):
        super().__init__("central_orchestrator", "Central Orchestrator")
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, Dict] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.registered_agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages and route them appropriately."""
        self.add_message_to_history(message)
        
        # Route message to appropriate handler based on message type
        if message.message_type == "user_request":
            return await self._handle_user_request(message)
        elif message.message_type == "agent_response":
            return await self._handle_agent_response(message)
        elif message.message_type == "workflow_update":
            return await self._handle_workflow_update(message)
        else:
            self.logger.warning(f"Unknown message type: {message.message_type}")
            return None
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a high-level task by coordinating multiple agents."""
        task_type = task.get("type")
        task_id = task.get("id", "unknown")
        
        self.update_state("processing", task_id)
        
        try:
            if task_type == "generate_learning_path":
                return await self._coordinate_path_generation(task)
            elif task_type == "reallocate_path":
                return await self._coordinate_reallocation(task)
            elif task_type == "process_voice_command":
                return await self._coordinate_voice_processing(task)
            elif task_type == "sync_integrations":
                return await self._coordinate_integration_sync(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.update_state("error")
            return {"status": "error", "message": str(e)}
        finally:
            self.update_state("idle")
    
    async def _handle_user_request(self, message: AgentMessage) -> AgentMessage:
        """Handle user requests by creating appropriate workflows."""
        request_type = message.content.get("request_type")
        user_id = message.content.get("user_id")
        
        if request_type == "generate_path":
            # Start path generation workflow
            workflow_id = await self._start_path_generation_workflow(message.content)
            return await self.send_message(
                message.sender,
                "workflow_started",
                {"workflow_id": workflow_id, "status": "initiated"}
            )
        
        # Add more request type handlers as needed
        return await self.send_message(
            message.sender,
            "error",
            {"message": f"Unknown request type: {request_type}"}
        )
    
    async def _coordinate_path_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate learning path generation across multiple agents."""
        user_profile = task.get("user_profile")
        goals = task.get("goals", [])
        
        # Step 1: Analyze user context
        context_agent = self.registered_agents.get("context_analyzer")
        if context_agent:
            context_result = await context_agent.execute_task({
                "type": "analyze_user_context",
                "user_profile": user_profile,
                "goals": goals
            })
        
        # Step 2: Generate path structure
        path_planner = self.registered_agents.get("path_planner")
        if path_planner:
            path_result = await path_planner.execute_task({
                "type": "generate_path_structure",
                "context": context_result,
                "goals": goals
            })
        
        # Step 3: Curate resources
        resource_curator = self.registered_agents.get("resource_curator")
        if resource_curator and path_result:
            curation_result = await resource_curator.execute_task({
                "type": "curate_milestone_resources",
                "milestones": path_result.get("milestones", [])
            })
        
        # Step 4: Optimize schedule
        schedule_optimizer = self.registered_agents.get("schedule_optimizer")
        if schedule_optimizer and path_result:
            schedule_result = await schedule_optimizer.execute_task({
                "type": "optimize_schedule",
                "path": path_result,
                "user_availability": user_profile.get("availability_schedule", {})
            })
        
        return {
            "status": "completed",
            "learning_path": path_result,
            "schedule": schedule_result,
            "resources": curation_result
        }
    
    async def _coordinate_reallocation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate learning path reallocation."""
        # TODO: Implement reallocation coordination
        return {"status": "completed", "message": "Reallocation coordinated"}
    
    async def _coordinate_voice_processing(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate voice command processing."""
        # TODO: Implement voice processing coordination
        return {"status": "completed", "message": "Voice command processed"}
    
    async def _coordinate_integration_sync(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate integration synchronization."""
        # TODO: Implement integration sync coordination
        return {"status": "completed", "message": "Integrations synchronized"}
    
    async def _start_path_generation_workflow(self, request_data: Dict[str, Any]) -> str:
        """Start a path generation workflow."""
        import uuid
        workflow_id = str(uuid.uuid4())
        
        self.active_workflows[workflow_id] = {
            "type": "path_generation",
            "status": "initiated",
            "request_data": request_data,
            "steps_completed": [],
            "current_step": "context_analysis"
        }
        
        return workflow_id
    
    def get_capabilities(self) -> List[str]:
        """Return orchestrator capabilities."""
        return [
            "workflow_coordination",
            "agent_management",
            "task_routing",
            "message_routing",
            "system_monitoring"
        ]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = {}
        for agent_id, agent in self.registered_agents.items():
            agent_statuses[agent_id] = agent.get_status()
        
        return {
            "orchestrator_status": self.get_status(),
            "registered_agents": len(self.registered_agents),
            "active_workflows": len(self.active_workflows),
            "agent_statuses": agent_statuses,
            "message_queue_size": self.message_queue.qsize()
        }