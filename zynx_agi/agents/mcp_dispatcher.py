"""
Model Context Protocol (MCP) Dispatcher
Central nervous system for routing and orchestrating agent interactions
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from .base_agent import ZynxAgent, AgentCapability, AgentResponse
from .agent_registry import AgentRegistry
import logging

logger = logging.getLogger(__name__)


class MCPDispatcher:
    """
    MCP Dispatcher - Parses user prompts and routes tasks to appropriate agents
    Handles slash commands (/agent:action) and @mentions (@context)
    """
    
    def __init__(self, agent_registry: AgentRegistry, storage_driver=None):
        self.registry = agent_registry
        self.storage = storage_driver
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.command_patterns = {
            "slash_command": re.compile(r'/(\w+):(\w+)(?:\s+(.+))?'),
            "mention": re.compile(r'@(\w+)(?:\s+(.+))?'),
            "pipeline": re.compile(r'(.+)\s*\|\s*(.+)')
        }
        
        # Agent routing table
        self.agent_routing = {
            "zynx": "zynx_main",
            "deeja": "deeja", 
            "metadata": "zynx_metadata",
            "main": "zynx_main",
            "cultural": "deeja",
            "emotional": "deeja",
            "compliance": "zynx_metadata",
            "governance": "zynx_metadata"
        }
        
        # Capability to agent mapping
        self.capability_routing = {
            AgentCapability.CHAT: ["zynx_main", "deeja"],
            AgentCapability.CULTURAL_ANALYSIS: ["deeja"],
            AgentCapability.EMOTIONAL_INTELLIGENCE: ["deeja"],
            AgentCapability.EMPATHY_SCORING: ["deeja"],
            AgentCapability.TRANSLATION: ["deeja"],
            AgentCapability.METADATA_MANAGEMENT: ["zynx_metadata"],
            AgentCapability.COMPLIANCE_MONITORING: ["zynx_metadata", "zynx_main"],
            AgentCapability.SESSION_MANAGEMENT: ["zynx_main", "zynx_metadata"]
        }
    
    async def dispatch_request(self, request: Dict[str, Any]) -> AgentResponse:
        """Main dispatch method for processing requests"""
        start_time = datetime.utcnow()
        
        try:
            # Parse the request to determine routing
            routing_info = await self._parse_request(request)
            
            # Execute the routing decision
            response = await self._execute_routing(request, routing_info)
            
            # Log dispatch operation
            if self.storage:
                await self.storage.store_log({
                    "action": "mcp_dispatch",
                    "routing_info": routing_info,
                    "success": response.success,
                    "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                    "timestamp": start_time.isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in MCP dispatcher: {e}")
            return AgentResponse(
                success=False,
                agent_id="mcp_dispatcher",
                response_data={"error": str(e), "routing_failed": True},
                timestamp=start_time.isoformat()
            )
    
    async def _parse_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Parse request to determine routing strategy"""
        message = request.get("message", "")
        
        routing_info = {
            "routing_type": "automatic",
            "target_agents": [],
            "commands": [],
            "mentions": [],
            "pipeline": False,
            "requires_orchestration": False
        }
        
        # Check for slash commands (/agent:action)
        slash_matches = self.command_patterns["slash_command"].findall(message)
        if slash_matches:
            routing_info["routing_type"] = "slash_command"
            for agent_name, action, params in slash_matches:
                routing_info["commands"].append({
                    "agent": agent_name,
                    "action": action,
                    "params": params if params else ""
                })
                
                # Map to actual agent ID
                actual_agent_id = self.agent_routing.get(agent_name.lower(), agent_name)
                if actual_agent_id not in routing_info["target_agents"]:
                    routing_info["target_agents"].append(actual_agent_id)
        
        # Check for @mentions (@context)
        mention_matches = self.command_patterns["mention"].findall(message)
        if mention_matches:
            for context, params in mention_matches:
                routing_info["mentions"].append({
                    "context": context,
                    "params": params if params else ""
                })
        
        # Check for pipeline operations (command1 | command2)
        pipeline_match = self.command_patterns["pipeline"].search(message)
        if pipeline_match:
            routing_info["pipeline"] = True
            routing_info["requires_orchestration"] = True
        
        # If no explicit routing, determine based on content analysis
        if not routing_info["target_agents"]:
            routing_info = await self._analyze_content_for_routing(message, routing_info)
        
        return routing_info
    
    async def _analyze_content_for_routing(
        self, 
        message: str, 
        routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze message content to determine optimal agent routing"""
        
        # Cultural/Thai content detection
        thai_indicators = ["ครับ", "ค่ะ", "สวัสดี", "ไทย", "วัฒนธรรม"]
        if any(indicator in message for indicator in thai_indicators):
            routing_info["target_agents"].append("deeja")
            routing_info["routing_type"] = "cultural_analysis"
        
        # Emotional content detection
        emotional_indicators = ["feeling", "emotion", "sad", "happy", "เศร้า", "ดีใจ"]
        if any(indicator in message.lower() for indicator in emotional_indicators):
            if "deeja" not in routing_info["target_agents"]:
                routing_info["target_agents"].append("deeja")
            routing_info["routing_type"] = "emotional_analysis"
        
        # Compliance/metadata keywords
        compliance_indicators = ["compliance", "metadata", "privacy", "license", "gdpr", "pdpa"]
        if any(indicator in message.lower() for indicator in compliance_indicators):
            routing_info["target_agents"].append("zynx_metadata")
            routing_info["routing_type"] = "compliance_check"
        
        # Default to main agent if no specific routing determined
        if not routing_info["target_agents"]:
            routing_info["target_agents"].append("zynx_main")
            routing_info["routing_type"] = "general_chat"
        
        return routing_info
    
    async def _execute_routing(
        self, 
        request: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> AgentResponse:
        """Execute the routing decision"""
        
        if routing_info["pipeline"]:
            return await self._execute_pipeline(request, routing_info)
        elif len(routing_info["target_agents"]) > 1:
            return await self._execute_multi_agent(request, routing_info)
        else:
            return await self._execute_single_agent(request, routing_info)
    
    async def _execute_single_agent(
        self, 
        request: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> AgentResponse:
        """Execute request on single agent"""
        
        if not routing_info["target_agents"]:
            raise ValueError("No target agents specified")
        
        agent_id = routing_info["target_agents"][0]
        agent = self.registry.get_agent(agent_id)
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # If slash command, execute specific capability
        if routing_info["routing_type"] == "slash_command" and routing_info["commands"]:
            command = routing_info["commands"][0]
            capability = self._map_action_to_capability(command["action"])
            
            if capability:
                return await agent.execute_capability(capability, {
                    "message": request.get("message", ""),
                    "params": command["params"],
                    **request
                })
        
        # Otherwise, process as general request
        return await agent.process_request(request)
    
    async def _execute_multi_agent(
        self, 
        request: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> AgentResponse:
        """Execute request across multiple agents with coordination"""
        
        responses = []
        orchestration_data = {
            "primary_response": None,
            "supporting_responses": [],
            "coordination_metadata": {}
        }
        
        # Determine primary agent (first in list or most specific)
        primary_agent_id = routing_info["target_agents"][0]
        primary_agent = self.registry.get_agent(primary_agent_id)
        
        if primary_agent:
            primary_response = await primary_agent.process_request(request)
            orchestration_data["primary_response"] = primary_response.response_data
            responses.append(primary_response)
        
        # Execute supporting agents
        for agent_id in routing_info["target_agents"][1:]:
            agent = self.registry.get_agent(agent_id)
            if agent:
                try:
                    response = await agent.process_request(request)
                    orchestration_data["supporting_responses"].append({
                        "agent_id": agent_id,
                        "response": response.response_data
                    })
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Error executing agent {agent_id}: {e}")
        
        # Orchestrate responses
        coordinated_response = await self._coordinate_responses(orchestration_data, routing_info)
        
        return AgentResponse(
            success=True,
            agent_id="mcp_dispatcher",
            response_data=coordinated_response,
            metadata={
                "orchestration_type": "multi_agent",
                "agents_involved": routing_info["target_agents"],
                "coordination_metadata": orchestration_data["coordination_metadata"]
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _execute_pipeline(
        self, 
        request: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> AgentResponse:
        """Execute pipeline of agent operations"""
        
        pipeline_result = {
            "pipeline_steps": [],
            "final_result": None,
            "intermediate_results": []
        }
        
        # For now, implement basic pipeline (would need more sophisticated parsing)
        current_data = request
        
        for i, agent_id in enumerate(routing_info["target_agents"]):
            agent = self.registry.get_agent(agent_id)
            if agent:
                try:
                    step_response = await agent.process_request(current_data)
                    
                    pipeline_result["pipeline_steps"].append({
                        "step": i + 1,
                        "agent_id": agent_id,
                        "success": step_response.success
                    })
                    
                    if step_response.success:
                        pipeline_result["intermediate_results"].append(step_response.response_data)
                        # Use response as input for next step
                        current_data = {
                            **request,
                            "previous_result": step_response.response_data
                        }
                    else:
                        # Pipeline failed at this step
                        pipeline_result["final_result"] = {
                            "error": f"Pipeline failed at step {i + 1}",
                            "failed_agent": agent_id
                        }
                        break
                        
                except Exception as e:
                    logger.error(f"Pipeline error at agent {agent_id}: {e}")
                    pipeline_result["final_result"] = {
                        "error": f"Pipeline error: {str(e)}",
                        "failed_agent": agent_id
                    }
                    break
        
        if not pipeline_result["final_result"]:
            pipeline_result["final_result"] = pipeline_result["intermediate_results"][-1] if pipeline_result["intermediate_results"] else {}
        
        return AgentResponse(
            success="error" not in pipeline_result["final_result"],
            agent_id="mcp_dispatcher",
            response_data=pipeline_result,
            metadata={"execution_type": "pipeline"},
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _coordinate_responses(
        self, 
        orchestration_data: Dict[str, Any], 
        routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate multiple agent responses"""
        
        coordinated = {
            "coordinated_response": "Multiple agents processed your request",
            "primary_agent_response": orchestration_data.get("primary_response", {}),
            "additional_insights": [],
            "routing_type": routing_info["routing_type"]
        }
        
        # Extract key insights from supporting responses
        for support_response in orchestration_data.get("supporting_responses", []):
            agent_id = support_response["agent_id"]
            response_data = support_response["response"]
            
            if agent_id == "deeja":
                # Extract cultural/emotional insights
                if "cultural_analysis" in response_data:
                    coordinated["additional_insights"].append({
                        "type": "cultural_intelligence",
                        "source": "deeja",
                        "data": response_data["cultural_analysis"]
                    })
                
                if "empathy_score" in response_data:
                    coordinated["additional_insights"].append({
                        "type": "empathy_scoring",
                        "source": "deeja", 
                        "score": response_data["empathy_score"]
                    })
            
            elif agent_id == "zynx_metadata":
                # Extract compliance insights
                if "compliance_status" in response_data:
                    coordinated["additional_insights"].append({
                        "type": "compliance_check",
                        "source": "zynx_metadata",
                        "status": response_data["compliance_status"]
                    })
        
        return coordinated
    
    def _map_action_to_capability(self, action: str) -> Optional[AgentCapability]:
        """Map action string to agent capability"""
        action_mapping = {
            "chat": AgentCapability.CHAT,
            "analyze": AgentCapability.CULTURAL_ANALYSIS,
            "cultural": AgentCapability.CULTURAL_ANALYSIS,
            "emotional": AgentCapability.EMOTIONAL_INTELLIGENCE,
            "empathy": AgentCapability.EMPATHY_SCORING,
            "translate": AgentCapability.TRANSLATION,
            "metadata": AgentCapability.METADATA_MANAGEMENT,
            "compliance": AgentCapability.COMPLIANCE_MONITORING,
            "session": AgentCapability.SESSION_MANAGEMENT
        }
        
        return action_mapping.get(action.lower())
    
    async def create_workflow(
        self, 
        workflow_id: str, 
        workflow_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a multi-step workflow"""
        
        workflow = {
            "id": workflow_id,
            "definition": workflow_definition,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "steps": workflow_definition.get("steps", []),
            "current_step": 0,
            "results": []
        }
        
        self.active_workflows[workflow_id] = workflow
        
        return {
            "workflow_created": True,
            "workflow_id": workflow_id,
            "steps_count": len(workflow["steps"])
        }
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a defined workflow"""
        
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "executing"
        
        try:
            for i, step in enumerate(workflow["steps"]):
                workflow["current_step"] = i
                
                # Execute step
                step_result = await self._execute_workflow_step(step, input_data)
                workflow["results"].append(step_result)
                
                # Use result as input for next step
                input_data = {**input_data, "previous_result": step_result}
            
            workflow["status"] = "completed"
            
            return {
                "workflow_completed": True,
                "workflow_id": workflow_id,
                "final_result": workflow["results"][-1] if workflow["results"] else None,
                "all_results": workflow["results"]
            }
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            
            return {
                "workflow_completed": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "completed_steps": len(workflow["results"])
            }
    
    async def _execute_workflow_step(
        self, 
        step: Dict[str, Any], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        agent_id = step.get("agent")
        action = step.get("action")
        params = step.get("params", {})
        
        # Construct request for agent
        request = {
            **input_data,
            **params,
            "workflow_step": True
        }
        
        # Route to appropriate agent
        routing_info = {
            "routing_type": "workflow_step",
            "target_agents": [agent_id],
            "commands": [{"agent": agent_id, "action": action, "params": params}]
        }
        
        response = await self._execute_routing(request, routing_info)
        
        return response.response_data
    
    async def get_active_workflows(self) -> Dict[str, Any]:
        """Get status of all active workflows"""
        
        workflows_status = {}
        
        for workflow_id, workflow in self.active_workflows.items():
            workflows_status[workflow_id] = {
                "status": workflow["status"],
                "current_step": workflow["current_step"],
                "total_steps": len(workflow["steps"]),
                "created_at": workflow["created_at"]
            }
        
        return workflows_status