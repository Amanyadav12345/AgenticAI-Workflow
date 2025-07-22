from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from amanfirstagent.tools.workflow_tools import (
    TruckSearchTool, 
    TripDetailCollectorTool, 
    TruckOwnerContactTool, 
    BiltyGeneratorTool,
    DocumentUploadTool,
    TripStatusTrackerTool,
    DriverVerificationTool,
    NotificationTool
)

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Amanfirstagent():
    """Amanfirstagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def trip_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['trip_planner'], # type: ignore[index]
            tools=[TruckSearchTool(), TripDetailCollectorTool(), NotificationTool()],
            verbose=True
        )

    @agent
    def availability_verifier(self) -> Agent:
        return Agent(
            config=self.agents_config['availability_verifier'], # type: ignore[index]
            tools=[TruckOwnerContactTool(), NotificationTool()],
            verbose=True
        )

    @agent
    def billing_documentation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['billing_documentation_agent'], # type: ignore[index]
            tools=[BiltyGeneratorTool(), DocumentUploadTool(), TripStatusTrackerTool(), 
                   DriverVerificationTool(), NotificationTool()],
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def trip_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['trip_planning_task'], # type: ignore[index]
        )

    @task
    def availability_verification_task(self) -> Task:
        return Task(
            config=self.tasks_config['availability_verification_task'], # type: ignore[index]
            context=[self.trip_planning_task()]
        )

    @task
    def billing_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['billing_documentation_task'], # type: ignore[index]
            context=[self.availability_verification_task()]
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Amanfirstagent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

    @crew
    def truck_booking_crew(self) -> Crew:
        """Creates the complete truck booking crew with all three agents"""
        return Crew(
            agents=[self.trip_planner(), self.availability_verifier(), self.billing_documentation_agent()],
            tasks=[self.trip_planning_task(), self.availability_verification_task(), self.billing_documentation_task()],
            process=Process.sequential,
            verbose=True,
        )
