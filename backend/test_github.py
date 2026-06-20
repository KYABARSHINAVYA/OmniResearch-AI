from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

g = Github(
    os.getenv("GITHUB_TOKEN")
)

repo = g.get_repo(
    "langchain-ai/langchain"
)

print(repo.name)
print(repo.stargazers_count)
print(repo.description)