from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
import os
from dotenv import load_dotenv
from utils.state import GlobalState
from utils.prompts import system_prompt
from utils.tools import search_api, extract_api
from langgraph.prebuilt import create_react_agent

load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY')

if not openai_key:
    raise ValueError("A OPENAI_API_KEY não foi encontrada. Verifique seu arquivo .env")

research_tools = [search_api, extract_api]

def researcher(state: dict):
    """
    Recebe o tópico, usa sua memória privada e as revisões mais recentes para coletar dados brutos.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_key
    )

    react_agent = create_react_agent(
        model=llm,
        tools=research_tools,
        prompt=system_prompt(agent="researcher")
    )

    messages_to_pass = list(state.get("researcher_memory", []))
    new_messages_to_memory = []

    if not messages_to_pass:
        # Primeiro ciclo: passamos apenas o tópico
        instruction = f"Topic: {state.get('topic', '')}"
        new_message = HumanMessage(content=instruction)
        messages_to_pass.append(new_message)
        new_messages_to_memory.append(new_message)
    else:
        # Ciclos seguintes: Já possui o tópico e o último rascunho, então precisa apenas das revisões
        instruction = ""
        if state.get("analyst_review"):
            instruction += f"Your last research was rejected by the Analyst. Fix these issues:\n{state.get('analyst_review')}\n"
        
        if state.get("reviewer_review"):
            instruction += f"The final report was rejected (Long-cycle). Reviewer context:\n{state.get('reviewer_review')}\n"
        
        if instruction:
            new_message = HumanMessage(content=instruction)
            messages_to_pass.append(new_message)
            new_messages_to_memory.append(new_message)

    react_agent_answer = react_agent.invoke({"messages": messages_to_pass})
    final_result = react_agent_answer["messages"][-1].content

    new_messages_to_memory.append(AIMessage(content=final_result))

    return {
        "raw_data": final_result, 
        "researcher_memory": new_messages_to_memory
    }

class AnalystOutput(BaseModel):
    critical_analysis: Optional[str] = Field(
        default="",
        description="The detailed critical analysis identifying patterns, contradictions, and gaps. Leave this EMPTY if you are rejecting the raw data (analyst_approval='NO')."
    )
    analyst_review: str = Field(
        description="Specific feedback detailing what is missing or wrong in the raw data. Leave empty or write 'None' if the data is perfect."
    )
    analyst_approval: str = Field(
        description="Respond strictly with 'YES' if the raw data is sufficient and good enough to be passed to the Writer. Respond 'NO' if it needs more research."
    )

def analyst(state: dict):
    """
    Recebe os dados brutos da pesquisa e retorna a análise crítica, a revisão da pesquisa e a aprovação.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_key 
    )

    structured_llm = llm.with_structured_output(AnalystOutput)

    instruction = f"Raw Data to analyze:\n{state.get('raw_data', '')}\n"

    # Caso ocorra um long-cycle é importante que o analista saiba o que foi rejeitado pelo revisor
    if state.get("reviewer_review"):
        instruction += f"\nATTENTION! The final intelligence report was rejected by the Reviewer for the following reason:\n{state.get('reviewer_review')}\nMake sure your new Critical Analysis specifically extracts data to address this gap."

    messages = [
        SystemMessage(content=system_prompt(agent="analyst")),
        HumanMessage(content=instruction)
    ]

    llm_answer = structured_llm.invoke(messages)

    cycle_1_counter = state.get("cycle_1_counter", 0)
    if llm_answer.analyst_approval == "NO":
        cycle_1_counter += 1
    else:
        cycle_1_counter = 0
    
    return {
        "critical_analysis": llm_answer.critical_analysis,
        "analyst_review": llm_answer.analyst_review,
        "analyst_approval": llm_answer.analyst_approval,
        "cycle_1_counter": cycle_1_counter
    }


def redactor(state: dict):
    """
    Recebe como entrada a análise crítica e a revisão do revisor e retorna o relatório de inteligência
    """
    llm = ChatOpenAI(
        model= "gpt-4o-mini",
        api_key=openai_key
    )

    messages_to_pass = list(state.get("redactor_memory", []))
    new_messages_to_memory = []

    if not messages_to_pass:
        # Primeiro ciclo: Passamos o tópico e a análise crítica
        instruction = f"Topic: {state.get('topic', '')}\nCritical analysis: {state.get('critical_analysis', '')}"
        new_message = HumanMessage(content=instruction)
        messages_to_pass.append(new_message)
        new_messages_to_memory.append(new_message)
    else:
        # Ciclos seguintes: Passamos a nova análise (se houver) e o feedback do revisor
        instruction = f"Critical analysis: {state.get('critical_analysis', '')}\n"

        if state.get("reviewer_review"):
            instruction += f"The final report was rejected. Reviewer context:\n{state.get('reviewer_review')}\n"
        
        if instruction:
            new_message = HumanMessage(content=instruction)
            messages_to_pass.append(new_message)
            new_messages_to_memory.append(new_message)
        
    full_messages = [SystemMessage(content=system_prompt(agent="redactor"))] + messages_to_pass
    
    llm_answer = llm.invoke(full_messages)

    new_messages_to_memory.append(AIMessage(content=llm_answer.content))

    return {
        "intelligence_report": llm_answer.content,
        "redactor_memory": new_messages_to_memory
    }

class ReviewerOutput(BaseModel):
    reviewer_review: Optional[str] = Field(
        default="",
        description="Specific, actionable feedback detailing logical errors, missing sections, or unsupported claims. Leave empty if the status is 'APPROVED'."
    )
    reviewer_approval: Literal["APPROVED", "WRITING_ERROR", "DATA_ERROR"] = Field(
        description="Classify the state of the report. 'APPROVED' if perfect. 'WRITING_ERROR' for formatting/logic issues. 'DATA_ERROR' if it lacks sources/facts/numbers."
    )

def reviewer(state: dict):
    """
    Avalia o relatório de pesquisa e retorna uma revisão e uma aprovação
    """

    llm = ChatOpenAI(
        model= "gpt-4o-mini",
        api_key= openai_key 
    )

    structured_llm = llm.with_structured_output(ReviewerOutput)

    instruction = f"Original Topic: {state.get('topic', '')}\n\nIntelligence Report to Evaluate:\n{state.get('intelligence_report', '')}"

    messages = [
        SystemMessage(content=system_prompt(agent="reviewer")),
        HumanMessage(content=instruction)
    ]

    llm_answer = structured_llm.invoke(messages)

    cycle_2_counter = state.get("cycle_2_counter", 0)
    cycle_3_counter = state.get("cycle_3_counter", 0)

    if llm_answer.reviewer_approval == "WRITING_ERROR":
        cycle_2_counter += 1
    elif llm_answer.reviewer_approval == "DATA_ERROR":
        cycle_3_counter += 1
    elif llm_answer.reviewer_approval == "APPROVED":
        cycle_2_counter = 0
        cycle_3_counter = 0
    
    return {
        "reviewer_review": llm_answer.reviewer_review,
        "reviewer_approval": llm_answer.reviewer_approval,
        "cycle_2_counter": cycle_2_counter,
        "cycle_3_counter": cycle_3_counter
    }

CYCLE_LIMIT = 3

def human_intervention(state: dict):
    """
    Nó de Human-in-the-Loop acionado quando o limite de ciclos é atingido.
    Contextualiza o humano sobre qual ciclo falhou e oferece opções específicas.
    """
    print("\n" + "="*70)
    print("⚠️  ALERTA DE LOOP: INTERVENÇÃO HUMANA NECESSÁRIA  ⚠️")
    print("="*70)

    cycle_1 = state.get("cycle_1_counter", 0)
    cycle_2 = state.get("cycle_2_counter", 0)
    cycle_3 = state.get("cycle_3_counter", 0)

    if cycle_1 >= CYCLE_LIMIT:
        print("🛑 PROBLEMA: O Analista está rejeitando repetidamente os dados do Pesquisador (Ciclo Curto 1).")
        print(f"Tópico: {state.get('topic')}")
        print(f"Última crítica do Analista:\n{state.get('analyst_review', 'Nenhuma')}")
        print("\nOpções de Intervenção:")
        print("1 - Aprovar os dados à força e forçar o avanço para o Redator.")
        print("2 - Fornecer uma instrução manual ao Pesquisador para uma nova busca.")
        print("3 - Abortar a execução.")

        action = input("\nEscolha uma ação (1-3): ")
        if action == "1":
            fallback_analysis = state.get("critical_analysis") or f"Human override. Base your report on these raw facts: {state.get('raw_data')}"
            return {"analyst_approval": "YES", "critical_analysis": fallback_analysis, "cycle_1_counter": 0, "human_route": "redactor"}
        elif action == "2":
            new_instruction = input("Digite a instrução direta para o Pesquisador: ")
            return {"analyst_review": new_instruction, "cycle_1_counter": 0, "human_route": "researcher"}
        else:
            raise Exception("Execução abortada pelo usuário.")

    elif cycle_2 >= CYCLE_LIMIT:
        print("🛑 PROBLEMA: O Revisor está rejeitando repetidamente a escrita do Redator (Ciclo Curto 2).")
        print(f"Última crítica do Revisor:\n{state.get('reviewer_review', 'Nenhuma')}")
        print("\nOpções de Intervenção:")
        print("1 - Aprovar o relatório à força e finalizar o processo.")
        print("2 - Fornecer uma instrução manual para o Redator reescrever.")
        print("3 - Abortar a execução.")

        action = input("\nEscolha uma ação (1-3): ")
        if action == "1":
            return {"reviewer_approval": "APPROVED", "cycle_2_counter": 0, "human_route": "end"}
        elif action == "2":
            new_instruction = input("Digite a instrução direta para o Redator: ")
            return {"reviewer_review": new_instruction, "cycle_2_counter": 0, "human_route": "redactor"}
        else:
            raise Exception("Execução abortada pelo usuário.")

    elif cycle_3 >= CYCLE_LIMIT:
        print("🛑 PROBLEMA: O Revisor está pedindo repetidamente mais dados ao Pesquisador (Ciclo Longo 3).")
        print(f"Última crítica do Revisor:\n{state.get('reviewer_review', 'Nenhuma')}")
        print("\nOpções de Intervenção:")
        print("1 - Aprovar o relatório ignorando a falta de dados e finalizar.")
        print("2 - Fornecer uma instrução manual ao Pesquisador para encontrar esses dados específicos.")
        print("3 - Redirecionar o erro para o Redator (mudar para WRITING_ERROR).")
        print("4 - Abortar a execução.")

        action = input("\nEscolha uma ação (1-4): ")
        if action == "1":
            return {"reviewer_approval": "APPROVED", "cycle_3_counter": 0, "human_route": "end"}
        elif action == "2":
            new_instruction = input("Digite a instrução para o Pesquisador: ")
            return {"reviewer_review": new_instruction, "cycle_3_counter": 0, "human_route": "researcher"}
        elif action == "3":
            new_instruction = input("Digite a instrução de formatação para o Redator: ")
            return {"reviewer_approval": "WRITING_ERROR", "reviewer_review": new_instruction, "cycle_3_counter": 0, "human_route": "redactor"}
        else:
            raise Exception("Execução abortada pelo usuário.")

    else:
        return {"human_route": "end"}