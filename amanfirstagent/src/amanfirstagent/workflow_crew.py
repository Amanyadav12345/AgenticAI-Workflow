"""
Enhanced CrewAI workflow system for agentic AI automation
Coordinates specialized agents to execute complex workflows
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from utils.logger import setup_logger, log_workflow_execution, log_agent_activity
from utils.security import SecurityManager
from .tools.workflow_tools import TripAPITool, APIIntegrationTool, DataValidationTool, NotificationTool

class WorkflowCrew:
    """
    Main workflow coordination system using CrewAI agents
    """
    
    def __init__(self):
        self.logger = setup_logger("workflow_crew")
        self.security_manager = SecurityManager()
        self.active_workflows = {}
        
        # Initialize tools
        self.trip_tool = TripAPITool()
        self.api_tool = APIIntegrationTool()
        self.validation_tool = DataValidationTool()
        self.notification_tool = NotificationTool()
        
        # Initialize the crew
        self.crew_instance = AgenticWorkflowCrew()
    
    async def execute_workflow(self, workflow_context: Dict) -> Dict:
        """
        Execute a workflow based on user request
        
        Args:
            workflow_context: Context containing user message and metadata
            
        Returns:
            Workflow execution result
        """
        workflow_id = str(uuid.uuid4())
        user_id = workflow_context.get('user_id')
        message = workflow_context.get('message')
        
        self.logger.info(f"Starting workflow {workflow_id} for user {user_id}")
        log_workflow_execution(self.logger, workflow_id, user_id, "started", "in_progress")
        
        try:
            # Store workflow context
            self.active_workflows[workflow_id] = {
                'context': workflow_context,
                'status': 'running',
                'start_time': datetime.now(),
                'steps': []
            }
            
            # Prepare inputs for CrewAI
            crew_inputs = {
                'user_message': message,
                'user_id': user_id,
                'workflow_id': workflow_id,
                'timestamp': workflow_context.get('timestamp', datetime.now().isoformat())
            }
            
            # Execute the crew
            result = await asyncio.to_thread(
                self.crew_instance.crew().kickoff,
                inputs=crew_inputs
            )
            
            # Process results
            workflow_result = self._process_crew_result(workflow_id, result)
            
            # Update workflow status
            self.active_workflows[workflow_id]['status'] = 'completed'
            self.active_workflows[workflow_id]['result'] = workflow_result
            
            log_workflow_execution(
                self.logger, workflow_id, user_id, "completed", "success",
                f"Summary: {workflow_result.get('summary', 'N/A')}"
            )
            
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            
            # Update workflow status
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]['status'] = 'failed'
                self.active_workflows[workflow_id]['error'] = str(e)
            
            log_workflow_execution(
                self.logger, workflow_id, user_id, "failed", "error", str(e)
            )
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'summary': 'Workflow execution failed'
            }
    
    def _process_crew_result(self, workflow_id: str, crew_result) -> Dict:
        """
        Process and format CrewAI execution results
        """
        try:
            # Extract result data based on CrewAI output format
            if hasattr(crew_result, 'output'):
                result_text = crew_result.output
            elif isinstance(crew_result, str):
                result_text = crew_result
            else:
                result_text = str(crew_result)
            
            # Try to parse as JSON if possible
            try:
                parsed_result = json.loads(result_text)
                if isinstance(parsed_result, dict):
                    return {
                        'success': True,
                        'workflow_id': workflow_id,
                        **parsed_result
                    }
            except json.JSONDecodeError:
                pass
            
            # Return formatted text result
            return {
                'success': True,
                'workflow_id': workflow_id,
                'summary': 'Workflow completed successfully',
                'details': result_text,
                'actions_taken': ['Workflow executed by AI agents']
            }
            
        except Exception as e:
            self.logger.error(f"Error processing crew result: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': f"Error processing results: {str(e)}",
                'summary': 'Result processing failed'
            }
    
    async def get_agents_status(self) -> Dict[str, str]:
        """
        Get status of all agents in the crew
        """
        try:
            # Check if crew is properly initialized
            crew = self.crew_instance.crew()
            
            status = {}
            
            # Check each agent
            for agent in crew.agents:
                agent_name = getattr(agent, 'role', 'Unknown Agent')
                try:
                    # Simple health check - try to access agent properties
                    if hasattr(agent, 'role') and hasattr(agent, 'goal'):
                        status[agent_name] = "healthy"
                    else:
                        status[agent_name] = "degraded"
                except Exception:
                    status[agent_name] = "unhealthy"
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking agent status: {e}")
            return {"error": f"Status check failed: {str(e)}"}
    
    def get_workflow_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get workflow execution history for a user
        """
        try:
            user_workflows = []
            
            for workflow_id, workflow_data in self.active_workflows.items():
                if workflow_data['context'].get('user_id') == user_id:
                    user_workflows.append({
                        'workflow_id': workflow_id,
                        'status': workflow_data['status'],
                        'start_time': workflow_data['start_time'].isoformat(),
                        'message': workflow_data['context'].get('message', 'N/A')[:100]
                    })
            
            # Sort by start time (most recent first)
            user_workflows.sort(key=lambda x: x['start_time'], reverse=True)
            
            return user_workflows[:limit]
            
        except Exception as e:
            self.logger.error(f"Error retrieving workflow history: {e}")
            return []


@CrewBase
class AgenticWorkflowCrew:
    """
    Enhanced CrewAI crew with specialized agents for workflow automation
    """
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def message_interpreter(self) -> Agent:
        return Agent(
            role="Message Interpreter and Intent Analyzer",
            goal="Understand user messages, extract intent, and identify required actions",
            backstory="""You are an expert at understanding natural language instructions 
            and converting them into structured workflow requirements. You can identify 
            the type of task, extract key parameters, and determine what systems or 
            operations are needed to fulfill the user's request.""",
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def workflow_orchestrator(self) -> Agent:
        return Agent(
            role="Workflow Orchestrator and Planner",
            goal="Plan and coordinate complex workflows across multiple systems",
            backstory="""You are a strategic workflow planner who can break down complex 
            tasks into manageable steps, coordinate between different systems, and ensure 
            all required actions are executed in the correct order. You understand 
            dependencies and can handle error scenarios gracefully.""",
            verbose=True,
            allow_delegation=True
        )
    
    @agent
    def api_integration_agent(self) -> Agent:
        return Agent(
            role="API Integration and External Systems Manager",
            goal="Handle all interactions with external APIs, databases, and systems",
            backstory="""You are an expert in system integration who can connect to 
            various APIs, execute database operations, and interact with external 
            services. You handle authentication, data transformation, and error 
            handling for all external integrations.""",
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def validation_agent(self) -> Agent:
        return Agent(
            role="Data Validation and Quality Assurance",
            goal="Validate data integrity and ensure workflow quality",
            backstory="""You are responsible for ensuring data quality, validating 
            inputs and outputs, checking for errors, and maintaining the integrity 
            of all workflow operations. You catch issues before they become problems.""",
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def trip_specialist_agent(self) -> Agent:
        return Agent(
            role="Trip Planning and Management Specialist",
            goal="Handle all trip-related operations including creation, updates, and management",
            backstory="""You are an expert travel agent who specializes in creating 
            and managing trips. You understand travel requirements, can parse trip 
            requests, validate travel data, and coordinate with booking systems to 
            create perfect travel experiences.""",
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def interpret_user_message(self) -> Task:
        return Task(
            description="""
            Analyze the user message: '{user_message}'
            
            Extract the following information:
            1. Intent/goal of the user
            2. Type of workflow required (data entry, report generation, system update, etc.)
            3. Key parameters and data points
            4. Target systems or databases that need to be involved
            5. Any specific requirements or constraints
            
            Provide a structured analysis in JSON format with these fields:
            - intent: brief description of what the user wants
            - workflow_type: category of workflow
            - parameters: extracted data and requirements
            - systems_needed: list of systems/APIs to interact with
            - complexity: simple/medium/complex
            - estimated_steps: number of steps required
            """,
            expected_output="JSON object containing structured analysis of user intent and requirements",
            agent=self.message_interpreter
        )
    
    @task
    def plan_workflow_execution(self) -> Task:
        return Task(
            description="""
            Based on the message interpretation, create a detailed execution plan.
            
            Create a step-by-step workflow plan that includes:
            1. Sequence of operations to be performed
            2. Dependencies between steps
            3. Error handling and rollback procedures
            4. Data validation checkpoints
            5. User feedback and confirmation points
            
            For each step, specify:
            - Action to be taken
            - Systems/APIs involved
            - Input data required
            - Expected output
            - Error handling strategy
            
            Return the plan as a structured JSON object.
            """,
            expected_output="Detailed workflow execution plan in JSON format",
            agent=self.workflow_orchestrator,
            context=[self.interpret_user_message]
        )
    
    @task
    def execute_workflow_steps(self) -> Task:
        return Task(
            description="""
            Execute the planned workflow steps systematically.
            
            For this simulation:
            1. Process each step in the execution plan
            2. Simulate API calls and system interactions
            3. Validate data at each step
            4. Handle any errors gracefully
            5. Provide detailed logs of actions taken
            
            Since this is a demonstration system, simulate the execution but provide 
            realistic feedback about what would happen in a real implementation.
            
            Return a comprehensive execution report.
            """,
            expected_output="Detailed execution report with results and actions taken",
            agent=self.api_integration_agent,
            context=[self.plan_workflow_execution]
        )
    
    @task
    def validate_and_summarize(self) -> Task:
        return Task(
            description="""
            Validate the workflow execution and create a user-friendly summary.
            
            Review the entire workflow execution and:
            1. Verify all steps were completed successfully
            2. Check data integrity and consistency
            3. Identify any issues or partial failures
            4. Create a clear, user-friendly summary
            5. Suggest any follow-up actions if needed
            
            Provide the final result in JSON format with:
            - success: boolean indicating overall success
            - summary: brief description of what was accomplished
            - details: more detailed breakdown
            - actions_taken: list of specific actions performed
            - next_steps: any recommended follow-up actions
            - issues: any problems encountered
            """,
            expected_output="Final workflow validation and user-friendly summary in JSON format",
            agent=self.validation_agent,
            context=[self.execute_workflow_steps]
        )
    
    @task
    def handle_trip_request(self) -> Task:
        return Task(
            description="""
            Handle trip-related requests specifically.
            
            Based on the interpreted message, if this is a trip-related request:
            1. Extract trip details (destination, dates, travelers, budget, preferences)
            2. Validate the trip data for completeness and accuracy
            3. Create the trip using the appropriate API
            4. Handle any booking confirmations or follow-up notifications
            5. Provide detailed trip information back to the user
            
            For trip creation, ensure you have:
            - Destination
            - Start and end dates
            - Number of travelers
            - Budget (if provided)
            - Any special preferences or requirements
            
            Return trip creation results with confirmation details.
            """,
            expected_output="Trip creation results with confirmation details and trip ID",
            agent=self.trip_specialist_agent,
            context=[self.interpret_user_message]
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the agentic workflow crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,  # Enable memory for better context retention
            planning=True  # Enable planning for complex workflows
        )