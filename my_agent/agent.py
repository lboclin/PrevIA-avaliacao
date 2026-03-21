from langgraph.graph import StateGraph, START, END
from utils.state import GlobalState
from utils.nodes import researcher, analyst, redactor, reviewer, human_intervention
import re
import os

# Define o limite de ciclos para a ativação da intervenção humana
CYCLE_LIMIT = 3

workflow = StateGraph(GlobalState)
workflow.add_node("researcher", researcher)
workflow.add_node("analyst", analyst)
workflow.add_node("redactor", redactor)
workflow.add_node("reviewer", reviewer)
workflow.add_node("human_intervention", human_intervention)

def route_analyst(state: GlobalState) -> str:
    """Verifica se o analista aprovou os dados brutos."""
    if state.get("cycle_1_counter", 0) >= CYCLE_LIMIT:
        return "human_intervention"

    if state.get("analyst_approval") == "YES":
        return "redactor"
    else:
        # Volta para o pesquisador se faltaram dados
        return "researcher"

def route_reviewer(state: GlobalState) -> str:
    """Verifica se o relatório final foi aprovado."""
    if state.get("cycle_2_counter", 0) >= CYCLE_LIMIT or state.get("cycle_3_counter", 0) >= CYCLE_LIMIT:
        return "human_intervention"

    if state.get("reviewer_approval") == "APPROVED":
        return END
    elif state.get("reviewer_approval") == "WRITING_ERROR":
        # Volta para o redator por erro de escrita
        return "redactor"
    else:
        # Volta para o pesquisador se faltaram dados
        return "researcher"
    
def route_human(state: GlobalState) -> str:
    """Lê a variável temporária gerada pelo input humano para rotear o fluxo."""
    route = state.get("human_route")
    if route == "end":
        return END
    elif route == "redactor":
        return "redactor"
    else:
        return "researcher"
    
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "analyst")

workflow.add_conditional_edges(
    "analyst",           
    route_analyst,       
    {                    
        "redactor": "redactor",
        "researcher": "researcher",
        "human_intervention": "human_intervention"
    }
)

workflow.add_edge("redactor", "reviewer")

workflow.add_conditional_edges(
    "reviewer",
    route_reviewer,
    {
        END: END,
        "redactor": "redactor",
        "researcher": "researcher",
        "human_intervention": "human_intervention"
    }
)

workflow.add_conditional_edges(
    "human_intervention",
    route_human,
    {
        END: END,
        "redactor": "redactor",
        "researcher": "researcher"
    }
)

app = workflow.compile()

def save_report_md(topic: str, content: str):
    safe_name = re.sub(r'[\\/*?:"<>|]', "", topic)
    archive_name = f"{safe_name.replace(' ', '_')}.md"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    reports_dir = os.path.join(root_dir, "intelligence_reports")
    
    os.makedirs(reports_dir, exist_ok=True)
    
    file_path = os.path.join(reports_dir, archive_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("\n" + "="*70)
    print(f"RELATÓRIO FINALIZADO E SALVO COM SUCESSO:\n{file_path}")
    print("="*70)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PREVIA: SISTEMA DE INTELIGÊNCIA DE PESQUISA")
    print("="*70)

    user_topic = input("\nDigite o tópico de pesquisa que deseja investigar: ")
    initial_state = {"topic": user_topic}

    final_state = None
    
    for step in app.stream(initial_state, stream_mode="values"):
        print(f"\n--- Estado atualizado ---")
        
        for key, value in step.items():
            if key in ["analyst_review", "reviewer_review", "analyst_approval", "reviewer_approval", "cycle_1_counter"]:
                print(f"\n[{key.upper()}]:")
                print(f"{value}")
            elif key in ["researcher_memory", "redactor_memory", "human_route"]:
                pass 
            else:
                print(f"[{key.upper()}]: {str(value)[:10]}...\n") 
        
        final_state = step

    if final_state and "intelligence_report" in final_state:
        save_report_md(user_topic, final_state["intelligence_report"])
    else:
        print("\nA execução foi encerrada antes da geração do relatório final.")
