
from dotenv import load_dotenv
from config.llm import invoke_llm

load_dotenv()



def reviewer(answer):
    prompt = f"""
Review and improve this answer. Fix mistakes, improve clarity:

{answer}
"""

    return invoke_llm(prompt, task="reviewer")
