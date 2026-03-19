def system_prompt(agent: str):
    if (agent == "researcher"):
        return "Act as a Senior Researcher..."
    elif (agent == "analyst"):
        return "Act as a Senior Data Analyst..."
    elif (agent == "redactor"):
        return "Act as a Senior Redactor..."
    elif (agent == "reviewer"):
        return "Act as a Senior Report Reviewer..."
    