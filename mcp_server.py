#!/usr/bin/env python3
"""
MCP Server for Agentic AI Workflow Tools
Provides workflow automation tools as MCP server functions
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from utils.logger import setup_logger
from utils.security import SecurityManager
from config import get_config
from amanfirstagent.src.amanfirstagent.tools.workflow_tools import (
    APIIntegrationTool,
    DataValidationTool,
    FileOperationTool,
    NotificationTool
)

class WorkflowMCPServer:
    """
    MCP Server providing workflow automation tools
    """
    
    def __init__(self):
        self.server = Server("workflow-tools")
        self.logger = setup_logger("mcp_server")
        self.security_manager = SecurityManager()
        self.config = get_config()
        
        # Initialize tools
        self.api_tool = APIIntegrationTool()
        self.validation_tool = DataValidationTool()
        self.file_tool = FileOperationTool()
        self.notification_tool = NotificationTool()
        
        # Register tools
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register all available tools with the MCP server"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools"""
            return [
                Tool(
                    name="create_trip",
                    description="Create a new trip using the trip API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "destination": {
                                "type": "string",
                                "description": "Trip destination"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Trip start date (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "Trip end date (YYYY-MM-DD)"
                            },
                            "travelers": {
                                "type": "integer",
                                "description": "Number of travelers"
                            },
                            "budget": {
                                "type": "number",
                                "description": "Trip budget"
                            },
                            "preferences": {
                                "type": "object",
                                "description": "Trip preferences and requirements"
                            }
                        },
                        "required": ["destination", "start_date", "end_date", "travelers"]
                    }
                ),
                Tool(
                    name="call_api",
                    description="Make HTTP requests to external APIs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "API endpoint URL"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                                "default": "GET",
                                "description": "HTTP method"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Request headers"
                            },
                            "payload": {
                                "type": "object",
                                "description": "Request payload/body"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30,
                                "description": "Request timeout in seconds"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="validate_data",
                    description="Validate data against specified rules and formats",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "description": "Data to validate"
                            },
                            "validation_rules": {
                                "type": "object",
                                "properties": {
                                    "required_fields": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of required fields"
                                    },
                                    "field_types": {
                                        "type": "object",
                                        "description": "Expected field types (email, phone, number, etc.)"
                                    },
                                    "business_rules": {
                                        "type": "array",
                                        "description": "Custom business validation rules"
                                    }
                                },
                                "description": "Validation rules to apply"
                            }
                        },
                        "required": ["data", "validation_rules"]
                    }
                ),
                Tool(
                    name="send_notification",
                    description="Send notifications via various channels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel": {
                                "type": "string",
                                "enum": ["email", "slack", "sms", "webhook"],
                                "description": "Notification channel"
                            },
                            "recipient": {
                                "type": "string",
                                "description": "Recipient (email, phone, webhook URL, etc.)"
                            },
                            "message": {
                                "type": "string",
                                "description": "Notification message"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Message subject (for email)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "normal", "high", "urgent"],
                                "default": "normal",
                                "description": "Notification priority"
                            }
                        },
                        "required": ["channel", "recipient", "message"]
                    }
                ),
                Tool(
                    name="process_file",
                    description="Handle file operations like reading, writing, and processing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["read", "write", "create", "process"],
                                "description": "File operation to perform"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to file"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write (for write operations)"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["txt", "json", "csv", "xml"],
                                "default": "txt",
                                "description": "File format"
                            }
                        },
                        "required": ["operation"]
                    }
                ),
                Tool(
                    name="parse_trip_request",
                    description="Parse natural language trip request and extract structured data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_message": {
                                "type": "string",
                                "description": "Natural language trip request"
                            }
                        },
                        "required": ["user_message"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """Handle tool calls"""
            try:
                self.logger.info(f"Tool called: {name} with arguments: {arguments}")
                
                # Security validation
                if not self._validate_tool_call(name, arguments):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "Security validation failed"
                        })
                    )]
                
                result = await self._execute_tool(name, arguments)
                
                return [TextContent(
                    type="text",
                    text=result
                )]
                
            except Exception as e:
                self.logger.error(f"Tool execution failed: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
    
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="workflow://config",
                    name="Workflow Configuration",
                    description="Current workflow system configuration",
                    mimeType="application/json"
                ),
                Resource(
                    uri="workflow://status",
                    name="System Status",
                    description="Current system status and health",
                    mimeType="application/json"
                ),
                Resource(
                    uri="workflow://templates",
                    name="Trip Templates",
                    description="Available trip request templates",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "workflow://config":
                return json.dumps({
                    "api_config": {
                        "gemini_model": self.config.api.gemini_model,
                        "trip_api_configured": bool(self.config.api.trip_api_url),
                        "request_timeout": self.config.api.request_timeout
                    },
                    "security_config": {
                        "max_message_length": self.config.security.max_message_length,
                        "session_timeout": self.config.security.session_timeout
                    },
                    "workflow_config": {
                        "max_concurrent": self.config.workflow.max_concurrent_workflows,
                        "timeout": self.config.workflow.workflow_timeout,
                        "memory_enabled": self.config.workflow.enable_memory
                    }
                })
            
            elif uri == "workflow://status":
                return json.dumps({
                    "system_health": "healthy",
                    "active_workflows": 0,
                    "last_check": "2025-07-22T09:42:34Z",
                    "tools_available": 6
                })
            
            elif uri == "workflow://templates":
                return json.dumps({
                    "trip_templates": [
                        {
                            "name": "Business Trip",
                            "template": "Create a business trip to {destination} from {start_date} to {end_date} for {travelers} people with budget {budget}"
                        },
                        {
                            "name": "Vacation",
                            "template": "Plan a vacation to {destination} from {start_date} to {end_date} for {travelers} travelers, budget {budget}, preferences: {preferences}"
                        },
                        {
                            "name": "Weekend Getaway",
                            "template": "Book a weekend trip to {destination} departing {start_date} returning {end_date} for {travelers} people"
                        }
                    ]
                })
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    def _validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Validate tool call for security"""
        try:
            # Basic validation
            if not tool_name or not isinstance(arguments, dict):
                return False
            
            # Validate string arguments
            for key, value in arguments.items():
                if isinstance(value, str):
                    if not self.security_manager.validate_message(value):
                        self.logger.warning(f"Security validation failed for {key}: {value[:50]}...")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute the specified tool"""
        
        if tool_name == "create_trip":
            return await self._create_trip(arguments)
        
        elif tool_name == "call_api":
            return await self._call_api(arguments)
        
        elif tool_name == "validate_data":
            return self.validation_tool._run(
                arguments.get("data", {}),
                arguments.get("validation_rules", {})
            )
        
        elif tool_name == "send_notification":
            return self.notification_tool._run(
                arguments.get("channel"),
                arguments.get("recipient"),
                arguments.get("message"),
                arguments.get("subject"),
                arguments.get("priority", "normal")
            )
        
        elif tool_name == "process_file":
            return self.file_tool._run(
                arguments.get("operation"),
                arguments.get("file_path"),
                arguments.get("content"),
                arguments.get("format", "txt")
            )
        
        elif tool_name == "parse_trip_request":
            return await self._parse_trip_request(arguments)
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _create_trip(self, arguments: Dict[str, Any]) -> str:
        """Create a trip using the configured API"""
        try:
            # Prepare trip payload
            trip_payload = {
                "destination": arguments.get("destination"),
                "start_date": arguments.get("start_date"),
                "end_date": arguments.get("end_date"),
                "travelers": arguments.get("travelers"),
                "budget": arguments.get("budget"),
                "preferences": arguments.get("preferences", {}),
                "created_via": "agentic_ai_workflow"
            }
            
            # Validate required fields
            validation_rules = {
                "required_fields": ["destination", "start_date", "end_date", "travelers"],
                "field_types": {
                    "start_date": "date",
                    "end_date": "date",
                    "travelers": "number"
                }
            }
            
            validation_result = json.loads(self.validation_tool._run(trip_payload, validation_rules))
            
            if not validation_result.get("valid"):
                return json.dumps({
                    "success": False,
                    "error": "Validation failed",
                    "validation_errors": validation_result.get("errors", [])
                })
            
            # Call trip API
            if self.config.api.trip_api_url:
                api_result = await self._call_api({
                    "url": self.config.api.trip_api_url,
                    "method": "POST",
                    "headers": {
                        "Authorization": f"Bearer {self.config.api.api_authentication_token}",
                        "Content-Type": "application/json"
                    },
                    "payload": trip_payload
                })
                
                return api_result
            else:
                # Simulate trip creation for demonstration
                return json.dumps({
                    "success": True,
                    "trip_id": f"trip_{hash(str(trip_payload)) % 100000}",
                    "message": "Trip created successfully (simulated)",
                    "trip_details": trip_payload,
                    "estimated_cost": arguments.get("budget", 0),
                    "confirmation_code": f"CONF{hash(str(trip_payload)) % 10000}"
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Trip creation failed: {str(e)}"
            })
    
    async def _call_api(self, arguments: Dict[str, Any]) -> str:
        """Make API call using the API integration tool"""
        return await asyncio.to_thread(
            self.api_tool._run,
            arguments.get("url"),
            arguments.get("method", "GET"),
            arguments.get("headers"),
            arguments.get("payload"),
            arguments.get("timeout", 30)
        )
    
    async def _parse_trip_request(self, arguments: Dict[str, Any]) -> str:
        """Parse natural language trip request"""
        user_message = arguments.get("user_message", "")
        
        try:
            # Simple NLP parsing for trip requests
            # In a real implementation, you'd use Gemini API here
            
            parsed_data = {
                "intent": "create_trip",
                "extracted_data": {},
                "confidence": 0.8
            }
            
            # Extract destination
            if " to " in user_message.lower():
                parts = user_message.lower().split(" to ")
                if len(parts) > 1:
                    destination = parts[1].split()[0].title()
                    parsed_data["extracted_data"]["destination"] = destination
            
            # Extract dates (basic pattern matching)
            import re
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            dates = re.findall(date_pattern, user_message)
            if len(dates) >= 2:
                parsed_data["extracted_data"]["start_date"] = dates[0]
                parsed_data["extracted_data"]["end_date"] = dates[1]
            
            # Extract number of travelers
            import re
            number_pattern = r'(\d+) (?:people|travelers|persons|guests)'
            match = re.search(number_pattern, user_message.lower())
            if match:
                parsed_data["extracted_data"]["travelers"] = int(match.group(1))
            
            # Extract budget
            budget_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
            match = re.search(budget_pattern, user_message)
            if match:
                budget_str = match.group(1).replace(',', '')
                parsed_data["extracted_data"]["budget"] = float(budget_str)
            
            return json.dumps({
                "success": True,
                "parsed_request": parsed_data,
                "original_message": user_message,
                "next_action": "create_trip" if parsed_data["extracted_data"] else "request_more_info"
            })
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Parsing failed: {str(e)}",
                "original_message": user_message
            })

async def main():
    """Main function to run the MCP server"""
    server_instance = WorkflowMCPServer()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("mcp_server")
    
    logger.info("Starting Workflow MCP Server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())