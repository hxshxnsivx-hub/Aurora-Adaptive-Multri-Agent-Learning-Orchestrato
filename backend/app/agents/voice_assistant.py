"""
Voice Assistant Agent for STT/TTS processing.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.integrations import elevenlabs_client

logger = logging.getLogger(__name__)


class VoiceAssistantAgent(BaseAgent):
    """Agent responsible for voice command processing and TTS generation."""
    
    def __init__(self):
        super().__init__(
            agent_id="voice_assistant_agent",
            name="Voice Assistant Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process voice assistant requests."""
        try:
            action = message.content.get("action")
            
            if action == "process_voice_command":
                return await self._process_voice_command(message, state)
            elif action == "generate_speech":
                return await self._generate_speech(message, state)
            elif action == "extract_intent":
                return await self._extract_intent(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in VoiceAssistantAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _process_voice_command(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process voice command and extract intent."""
        transcript = message.content.get("transcript", "")
        confidence = message.content.get("confidence", 0.0)
        
        # Extract intent from transcript
        intent = self._extract_intent_from_text(transcript)
        entities = self._extract_entities(transcript)
        
        # Generate appropriate response
        response_text = self._generate_response_text(intent, entities, state)
        
        # Generate speech using ElevenLabs API
        try:
            audio_data = await elevenlabs_client.text_to_speech(
                text=response_text,
                model_id="eleven_monolingual_v1"
            )
            
            # In production, would upload to S3/R2 and return URL
            # For now, return base64 encoded audio or placeholder
            audio_url = "data:audio/wav;base64,..." if audio_data else None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            audio_url = None
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "transcript": transcript,
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "response_text": response_text,
                "audio_url": audio_url,
                "actions": self._determine_actions(intent, entities)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _generate_speech(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Generate speech from text using TTS."""
        text = message.content.get("text", "")
        voice_id = message.content.get("voice_id")
        
        try:
            # Generate speech using ElevenLabs
            audio_data = await elevenlabs_client.text_to_speech(
                text=text,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1"
            )
            
            # In production, would upload to S3/R2 and return URL
            audio_url = "data:audio/wav;base64,..." if audio_data else None
            
            # Estimate duration (rough: ~150 words per minute, ~5 chars per word)
            duration_seconds = len(text) / (150 * 5 / 60)
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            audio_url = None
            duration_seconds = 0
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "text": text,
                "audio_url": audio_url,
                "voice_id": voice_id or "default",
                "duration_seconds": duration_seconds
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _extract_intent(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Extract intent from text."""
        text = message.content.get("text", "")
        
        intent = self._extract_intent_from_text(text)
        entities = self._extract_entities(text)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "intent": intent,
                "entities": entities,
                "confidence": 0.85
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _extract_intent_from_text(self, text: str) -> str:
        """Extract intent from text using simple pattern matching."""
        text_lower = text.lower()
        
        # Intent patterns
        if any(word in text_lower for word in ["what", "show", "tell me"]):
            if "study" in text_lower or "learn" in text_lower:
                return "get_study_plan"
            elif "progress" in text_lower:
                return "get_progress"
            elif "next" in text_lower:
                return "get_next_task"
        
        elif any(word in text_lower for word in ["reschedule", "move", "change"]):
            return "reschedule_task"
        
        elif any(word in text_lower for word in ["help", "stuck", "difficult"]):
            return "request_help"
        
        elif any(word in text_lower for word in ["complete", "done", "finished"]):
            return "mark_complete"
        
        return "general_query"
    
    def _extract_entities(self, text: str) -> Dict:
        """Extract entities from text."""
        entities = {}
        text_lower = text.lower()
        
        # Extract time entities
        if "today" in text_lower:
            entities["time"] = "today"
        elif "tomorrow" in text_lower:
            entities["time"] = "tomorrow"
        elif "this week" in text_lower:
            entities["time"] = "this_week"
        
        # Extract topic entities
        topics = ["python", "javascript", "algorithms", "data structures", "machine learning"]
        for topic in topics:
            if topic in text_lower:
                entities["topic"] = topic
                break
        
        return entities
    
    def _generate_response_text(self, intent: str, entities: Dict, state: AgentState) -> str:
        """Generate appropriate response text based on intent."""
        responses = {
            "get_study_plan": "Here's your study plan for today. You have 3 tasks scheduled: Python basics at 9 AM, Data structures at 2 PM, and Algorithms practice at 5 PM.",
            "get_progress": "You've completed 15 out of 50 tasks, that's 30% progress. You're on a 7-day streak! Keep it up!",
            "get_next_task": "Your next task is to study Python basics. It's scheduled for 30 minutes and includes a video tutorial.",
            "reschedule_task": "I can help you reschedule that. When would you like to move it to?",
            "request_help": "I understand you're having difficulty. Let me find some additional resources and easier materials for you.",
            "mark_complete": "Great job! I've marked that task as complete. Your next task is ready when you are.",
            "general_query": "I'm here to help with your learning journey. You can ask me about your study plan, progress, or request to reschedule tasks."
        }
        
        return responses.get(intent, "I'm not sure I understood that. Could you rephrase?")
    
    def _determine_actions(self, intent: str, entities: Dict) -> List[Dict]:
        """Determine actions to take based on intent."""
        actions = []
        
        if intent == "get_study_plan":
            actions.append({"type": "fetch_tasks", "params": {"time": entities.get("time", "today")}})
        
        elif intent == "get_progress":
            actions.append({"type": "fetch_progress", "params": {}})
        
        elif intent == "reschedule_task":
            actions.append({"type": "initiate_reschedule", "params": entities})
        
        elif intent == "request_help":
            actions.append({"type": "trigger_reallocation", "params": {"reason": "difficulty"}})
        
        elif intent == "mark_complete":
            actions.append({"type": "update_task_status", "params": {"status": "completed"}})
        
        return actions
