from langgraph.graph import StateGraph, START, END
from utils.state import GlobalState
from utils.nodes import researcher, analyst, redactor, reviewer

workflow = StateGraph(GlobalState)

workflow.add_node("researcher", researcher)
workflow.add_node("analyst", analyst)
workflow.add_node("redactor", redactor)
workflow.add_node("reviewer", reviewer)

def route_analyst(state: GlobalState) -> str:
    """Verifica se o analista aprovou os dados brutos."""
    if state.get("analyst_approval") == "YES":
        return "redactor"
    else:
        # Volta para o pesquisador se faltaram dados
        # Aqui terá a adição da contagem do ciclo 1
        return "researcher"

def route_reviewer(state: GlobalState) -> str:
    """Verifica se o relatório final foi aprovado."""
    if state.get("reviewer_approval") == "APPROVED":
        return END
    elif state.get("reviewer_approval") == "WRITING_ERROR":
        # Aqui terá a adição da contagem dos ciclo 2
        return "redactor"
    else:
        # Aqui terá a adição da contagem dos ciclo 3
        return "researcher"
    
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "analyst")

workflow.add_conditional_edges(
    "analyst",           
    route_analyst,       
    {                    
        "redactor": "redactor",
        "researcher": "researcher"
    }
)

workflow.add_edge("redactor", "reviewer")

workflow.add_conditional_edges(
    "reviewer",
    route_reviewer,
    {
        END: END,
        "redactor": "redactor",
        "researcher": "researcher"
    }
)

app = workflow.compile()

if __name__ == "__main__":
    print("Iniciando a execução do pipeline...")

    # Input do usuário
    initial_state = {"topic": "A bolha da Inteligência Artificial"}
    
    for step in app.stream(initial_state, stream_mode="values"):
        # Mostra qual chave do estado foi atualizada por último para acompanharmos o fluxo
        print(f"\n--- Estado atualizado ---")
        for key, value in step.items():
            print(f"{key}: {str(value)[:100]}...")
