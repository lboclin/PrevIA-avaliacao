from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional
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

    messages_to_pass = state.get("researcher_memory", [])
    new_messages_to_memory = []

    if not messages_to_pass:
        # Se a memória está vazia, é o primeiro ciclo, então passamos apenas o tópico
        instruction = f"Topic: {state.get('topic', '')}"
        new_message = HumanMessage(content=instruction)
        messages_to_pass.append(new_message)
        new_messages_to_memory.append(new_message)
    else:
        # Se já tem memória, ele já sabe o tópico e lembra do seu último rascunho, só precisa das revisões
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

    # Atualizamos a memória privada apenas com o resultado final, sem armazenar o "lixo" gerado pelo loop ReAct
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
    
    return {
        "critical_analysis": llm_answer.critical_analysis,
        "analyst_review": llm_answer.analyst_review,
        "analyst_approval": llm_answer.analyst_approval
    }


def redactor(state: dict):
    """
    Recebe como entrada a análise crítica e a revisão do revisor e retorna o relatório de inteligência
    """
    llm = ChatOpenAI(
        model= "gpt-4o-mini",
        api_key=openai_key
    )

    messages = [
        SystemMessage(content=system_prompt(agent="redactor")),
        HumanMessage(content=f"Topic: {state.get('topic', '')}\nCritical analysis: {state.get('critical_analysis', '')}\nReviewer review (if exists): {state.get('reviewer_review', '')}\nLast intelligence report: {state.get('intelligence_report', '')}")
    ]

    llm_answer = llm.invoke(messages)

    return {
        "intelligence_report": llm_answer.content
    }

class ReviewerOutput(BaseModel):
    reviewer_review: str = Field(
        description="Specific, actionable feedback detailing logical errors, missing sections, or unsupported claims in the report. Leave empty or write 'None' if the report is perfect."
    )
    reviewer_approval: str = Field(
        description="Respond strictly with 'YES' if the report meets all quality standards and has all required sections. Respond 'NO' if it needs to be rewritten."
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

    messages = [
        SystemMessage(content=system_prompt(agent="reviewer")),
        HumanMessage(content=state.get("intelligence_report", ""))
    ]

    llm_answer = structured_llm.invoke(messages)
    
    return {
        "reviewer_review": llm_answer.reviewer_review,
        "reviewer_approval": llm_answer.reviewer_approval
    }