import pytest
from supply_chain_optimization.crews.fetch_graphdb_crew.fetch_graphdb_crew import FetchGraphdbCrew
from supply_chain_optimization.crews.inventory_monitoring_crew.inventory_monitoring_crew import InventoryMonitoringCrew
from dotenv import load_dotenv
from crewai.project import crew
from crewai import Crew, Process 
import json


load_dotenv()

@pytest.fixture
def fetch_garph_db_crew():
    test_crew_base = FetchGraphdbCrew()
    
    agents_subset = [
        test_crew_base.graph_db_specialist()
    ]

    tasks_subset = [
        test_crew_base.fetch_graph_db()
    ]

    partial_crew = Crew(
        agents= agents_subset,
        tasks=tasks_subset,
        process=Process.sequential,
        verbose=True

    )
    return partial_crew

@pytest.fixture
def monitor_inventory_crew():
    test_crew_base = InventoryMonitoringCrew()
    
    agents_subset = [
        test_crew_base.inventory_agent()
    ]

    tasks_subset = [
        test_crew_base.fetch_graph_db()
    ]

    partial_crew = Crew(
        agents= agents_subset,
        tasks=tasks_subset,
        process=Process.sequential,
        verbose=True

    )

    pass



    return partial_crew



def test_fetch_graph_db(fetch_garph_db_crew):

    inputs = {

    }
    result = fetch_garph_db_crew.kickoff(inputs=inputs)
    assert len(result.tasks_output) == 1
    raw_output = result.tasks_output[0].raw
    print("[test_fetch_graph_db] output:\n", raw_output)
    costs = 0.150 * (fetch_garph_db_crew.usage_metrics.prompt_tokens + fetch_garph_db_crew.usage_metrics.completion_tokens) / 1_000_000
    print(f"Total costs: ${costs:.4f}")