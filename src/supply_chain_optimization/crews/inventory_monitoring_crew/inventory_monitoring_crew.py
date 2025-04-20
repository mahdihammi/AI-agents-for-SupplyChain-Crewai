from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from supply_chain_optimization.tools.custom_tool import GraphManagerTool, SnowflakeClientTool
import os
from dotenv import load_dotenv

load_dotenv()




@CrewBase
class InventoryMonitoringCrew():
    """InventoryMonitoringCrew crew"""


    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def inventory_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['inventory_agent'],
            verbose=True
        )

    @task
    def sql_creation_and_execution(self) -> Task:
        return Task(
            config=self.tasks_config['sql_creation_and_execution'],
            tools=[SnowflakeClientTool()]

        )

    @crew
    def crew(self) -> Crew:
        """Creates the InventoryMonitoringCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            output_log_file="crew"
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )


