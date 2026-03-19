from langchain_core.messages import AnyMessage
from typing import TypedDict, Annotated
import operator

class GlobalState(TypedDict):
    topic: str
    raw_data: str
    critical_analysis: str
    intelligence_report: str

    analyst_review: str
    analyst_approval: str
    reviewer_review: str
    reviewer_approval: str


    cycle_1_counter: int # Short-cycle: Analyst -> Researcher
    cycle_2_counter: int # Short-cycle: Reviewer -> Redactor
    cycle_3_counter: int # Long-cycle: Reviewer -> Researcher 

