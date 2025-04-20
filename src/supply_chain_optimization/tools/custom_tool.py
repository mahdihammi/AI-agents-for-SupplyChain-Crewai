from typing import Type
import sys, os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath("../"))  # Add "projects" to sys.path

from supply_chain_optimization.utils.graph_manager import GraphManager
from supply_chain_optimization.utils.snowflake_client import SnowflakeClient

class GraphManagerTool(BaseTool):
    name: str = "GraphManagerTool"
    description: str=""

    def __init__(self, uri: str, **kwargs):
        super().__init__(**kwargs)
        self._gm = GraphManager(uri)

    def _run(self, cypher: str):
        #cypher_query = "MATCH p = (k:KPI)-[*0..]->(m:Metric) RETURN p"
        #cypher_query = """MATCH p = (k:KPI)-[:HAS_METRIC]->(m:Metric)-[:HAS_DIMENSION*0..1]->(dim:Dimension)-[:DERIVED_FROM*0..1]->(t:Table)
            #RETURN p"""
        paths_data = self._gm.get_paths_from_neo4j(cypher_query=cypher)
        tree_data = self._gm.collect_arbitrary_tree_for_llm(paths_data)
        tree_data = json.dumps(tree_data)
        return tree_data
    


######################### SnowflakeClientTool ########################""
class SQLQueryInput(BaseModel):
    sql: str = Field(..., description="SQL query to execute on Snowflake.")


class SnowflakeClientTool(BaseTool):
    name: str = "snowflake_client_tool"
    description: str = "Executes SQL queries on Snowflake and returns rows."

    args_schema: Type[BaseModel] = SQLQueryInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = SnowflakeClient()  # uses .env for credentials

    def _run(self, sql: str):
        rows = self._client.execute_query(sql)
        # Possibly convert to JSON
        return {"rows": rows}
    




#uri = os.getenv('NEO4j_URI')
#gm = GraphManagerTool(uri=uri)
#result = gm._run("""
#                    MATCH p = (s:Schema)-[*0..]->(c:Column) RETURN p"""
#                 )
#print(result)


