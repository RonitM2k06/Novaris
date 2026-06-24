from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import os
import glob

# Import backend engine
from novaris.state import StateManager
from test_ontology_expansion import build_expanded_graph, build_expanded_scenarios
from novaris.sticky_simulation import StickySimulationEngine

app = FastAPI(title="Novaris Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_expanded_graph()
historical_scenarios = {s.name: s for s in build_expanded_scenarios()}

class SimulationRequest(BaseModel):
    shocks: Dict[str, float]
    duration: int = 10

@app.post("/simulate")
def simulate(request: SimulationRequest):
    manager = StateManager()
    manager.base_graph = graph
    state = manager.create_scenario("Custom Simulation")
    engine = StickySimulationEngine(state)
    
    for node_id, delta in request.shocks.items():
        engine.inject_shock(node_id, delta)
        
    simulated_outcomes = {}
    for node_id in graph.nodes.keys():
        history = [h for h in state.history if h['node_id'] == node_id]
        if history:
            net_change = (history[-1]['new_value'] - history[0]['old_value']) / history[0]['old_value']
            simulated_outcomes[node_id] = net_change
        else:
            simulated_outcomes[node_id] = 0.0
            
    return {
        "outcomes": simulated_outcomes,
        "history": state.history
    }

class ReplayRequest(BaseModel):
    scenario_name: str

@app.post("/historical-replay")
def historical_replay(request: ReplayRequest):
    if request.scenario_name not in historical_scenarios:
        return {"error": "Scenario not found"}
        
    scenario = historical_scenarios[request.scenario_name]
    
    manager = StateManager()
    manager.base_graph = graph
    state = manager.create_scenario(scenario.name)
    engine = StickySimulationEngine(state)
    
    for node_id, delta in scenario.initial_shocks.items():
        engine.inject_shock(node_id, delta)
        
    simulated_outcomes = {}
    for node_id in graph.nodes.keys():
        history = [h for h in state.history if h['node_id'] == node_id]
        if history:
            net_change = (history[-1]['new_value'] - history[0]['old_value']) / history[0]['old_value']
            simulated_outcomes[node_id] = net_change
        else:
            simulated_outcomes[node_id] = 0.0
            
    from novaris.historical_replay import ReplayEvaluationMetrics
    metrics = ReplayEvaluationMetrics.evaluate(scenario.expected_outcomes, simulated_outcomes)
    
    # Convert expected outcomes to dict for easy frontend consumption
    expected_dict = {exp.node_id: exp.expected_pct_change for exp in scenario.expected_outcomes}
    
    return {
        "scenario": {
            "name": scenario.name,
            "year": scenario.year,
            "description": scenario.description,
            "initial_shocks": scenario.initial_shocks
        },
        "expected": expected_dict,
        "simulated": simulated_outcomes,
        "metrics": metrics,
        "history": state.history
    }

@app.get("/ontology")
def get_ontology():
    nodes = []
    for node_id, node in graph.nodes.items():
        nodes.append({
            "id": node.id,
            "name": node.name,
            "category": node.category,
            "value": node.current_value
        })
        
    edges = []
    for node_id in graph.adjacency_list:
        for edge in graph.adjacency_list[node_id]:
            edges.append({
                "source": node_id,
                "target": edge.target_id,
                "strength": edge.strength,
                "confidence": edge.confidence,
                "lag": edge.lag
            })
            
    return {
        "nodes": nodes,
        "edges": edges
    }

@app.get("/reports")
def get_reports():
    import pathlib
    # Root of the repository is one level up from src/
    repo_root = pathlib.Path(__file__).parent.parent
    reports_dir = repo_root / "docs"
    
    reports = []
    if reports_dir.exists() and reports_dir.is_dir():
        for file_path in reports_dir.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            reports.append({
                "filename": file_path.name,
                "content": content
            })
    return {"reports": reports}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
