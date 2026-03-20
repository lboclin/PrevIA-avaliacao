from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from utils.state import GlobalState
from utils.prompts import system_prompt

load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY')

if not openai_key:
    raise ValueError("A OPENAI_API_KEY não foi encontrada. Verifique seu arquivo .env")

def researcher(state: dict):
    """
    Recebe o tópico, as possíveis revisões do analista e do revisor e retorna os dados brutos coletados
    """
    llm = ChatOpenAI(
        model= "gpt-4o-mini",
        api_key=openai_key
    )

    messages = [
        SystemMessage(content=system_prompt(agent="researcher")),
        HumanMessage(content=f"Topic: {state.get('topic', '')}\nLast research: {state.get('raw_data', '')}\nAnalyst review (if exists): {state.get('analyst_review', '')}\nReviewer review (if exists): {state.get('reviewer_review', '')}")
    ]

    llm_answer = llm.invoke(messages)

    return {
        "raw_data": llm_answer.content
    }

class AnalystOutput(BaseModel):
    critical_analysis: str = Field(
        description="The detailed critical analysis identifying patterns, contradictions, and gaps based on the raw data."
    )
    analyst_review: str = Field(
        description="Specific feedback detailing what is missing or wrong in the raw data. Leave empty or write 'None' if the data is perfect."
    )
    analyst_approval: str = Field(
        description="Respond strictly with 'YES' if the raw data is sufficient and good enough to be passed to the Writer. Respond 'NO' if it needs more research."
    )

def analyst(state: dict):
    """
    Recebe os dados brutos da pesquisa e retorna a análise crítica (se for possível), a revisão da pesquisa e a aprovação
    """

    llm = ChatOpenAI(
        model= "gpt-4o-mini",
        api_key= openai_key 
    )

    structured_llm = llm.with_structured_output(AnalystOutput)

    messages = [
        SystemMessage(content=system_prompt(agent="analyst")),
        HumanMessage(content=state.get("raw_data", ""))
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