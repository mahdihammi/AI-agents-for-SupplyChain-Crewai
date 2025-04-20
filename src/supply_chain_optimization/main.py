#!/usr/bin/env python
from ast import Dict
from random import randint
from typing import Any, List

from pydantic import BaseModel

from crewai.flow import Flow, listen, start, and_, or_

from supply_chain_optimization.crews.inventory_monitoring_crew.inventory_monitoring_crew import InventoryMonitoringCrew
from supply_chain_optimization.crews.find_supplier_crew.find_supplier_crew import FindSupplierCrew
from supply_chain_optimization.crews.fetch_graphdb_crew.fetch_graphdb_crew import FetchGraphdbCrew
from supply_chain_optimization.crews.find_best_route_crew.find_best_route_crew import FindBestRouteCrew
from supply_chain_optimization.crews.email_generator_crew.email_generator_crew import EmailGeneratorCrew
from supply_chain_optimization.crews.report_writer_crew.report_writer_crew import ReportWriterCrew

import mlflow

mlflow.crewai.autolog()

# Optional: Set a tracking URI and an experiment name if you have a tracking server
mlflow.set_tracking_uri("http://127.0.0.1:8000")
mlflow.set_experiment("CrewAI")
from dotenv import load_dotenv

load_dotenv()


#######################""

class SupplyChainState(BaseModel):
    products : dict[str, Any] = {} 
    supplier : dict[str, Any] = {}
    graph_db : str = ""
    route : dict[str, Any] = {} 
    email : str = ""
    report : str = ""

# Ahmed snene
class SupplyChainFlow(Flow[SupplyChainState]):
    @start()
    def fetch_graph_db(self):
        graph_db = (
            FetchGraphdbCrew().crew().kickoff(inputs={})
        )
        self.state.graph_db = graph_db.raw

    @listen(fetch_graph_db)
    def monitor_inventory(self):
        print("monitoring inventory")
        inputs = {
            "graph_path" : self.state.graph_db
        }
        result = ( 
            InventoryMonitoringCrew().crew().kickoff(inputs=inputs) 
            
            )
        self.state.products = result.raw

        print(self.state.products)
    
    @listen(monitor_inventory)
    def select_supplier(self):
        inputs = {
            "products" : self.state.products,
            "graph_path" : self.state.graph_db
        }
        supplier = (
            FindSupplierCrew().crew().kickoff(inputs=inputs)
        )

        self.state.supplier = supplier.raw
    
    @listen(select_supplier)
    def find_best_route(self):
        inputs = {
            "graph_path" : self.state.graph_db,
            "supplier" : self.state.supplier
        }
        route = (
                FindBestRouteCrew().crew().kickoff(inputs=inputs)
        )
        self.state.route = route.raw

    @listen(find_best_route)
    def generate_email(self):
        inputs = {
            "products": self.state.products,
            "supplier" : self.state.supplier,
            "route" : self.state.route
        }
        email = (
                EmailGeneratorCrew().crew().kickoff(inputs=inputs)
        )
        self.state.email = email.raw

    @listen(generate_email)
    def report_writing(self):
        inputs = {
             "products": self.state.products,
            "supplier" : self.state.supplier,
            "route" : self.state.route
        }
        report = (
            ReportWriterCrew().crew().kickoff(inputs=inputs)
        )

        self.state.report = report.raw

    


    @listen(or_(generate_email, report_writing))
    def save_all_results(self):
        with open("output.txt", "a+") as file:
            file.write("\n**********************************\n")
            file.write(self.state.products)
        with open("supplier.txt", "a+") as file:
            file.write("\n*********************************\n")
            file.write(self.state.supplier)
        with open("route.txt", "a+") as file:
            file.write("\n******************************\n")
            file.write(self.state.route)
        with open("email.txt", "a+") as file:
            file.write("\n******************************\n")
            file.write(self.state.email)
        with open("route.md", "a") as file:
            file.write("\n******************************\n")
            file.write(self.state.report)
 




def kickoff():
    poem_flow = SupplyChainFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = SupplyChainFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
