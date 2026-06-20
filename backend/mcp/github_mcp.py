from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

g = Github(
    os.getenv(
        "GITHUB_TOKEN"
    )
)


def github_repo(repo_name):

    try:

        repo = g.get_repo(
            repo_name
        )

        return {

            "name": repo.name,
            "stars": repo.stargazers_count,
            "description": repo.description

        }

    except Exception:

        return {}