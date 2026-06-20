
from dotenv import load_dotenv
from config.llm import llm

load_dotenv()



def supervisor(question):

    prompt = f"""
    User question:

    {question}

    Decide which agents are needed among:

    Planner
    Research
    Writer
    Reviewer
    """

    response = llm.invoke(prompt)

    return response.content