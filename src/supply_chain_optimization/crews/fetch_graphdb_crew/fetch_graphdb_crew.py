from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from supply_chain_optimization.tools.custom_tool import GraphManagerTool, SnowflakeClientTool
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FetchGraphdbCrew():
    """FetchGraphdbCrew crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def graph_db_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['graph_db_specialist'],
            verbose=True, 
            tools=[GraphManagerTool(uri=os.getenv('NEO4J_URI'), result_as_answer=True)]
        )

    @task
    def fetch_graph_db(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_graph_db'],
            verbose=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FetchGraphdbCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
