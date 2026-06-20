import os
import traceback
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    content: str
    provider: str = "fallback"
    model: str = "none"


class RoutedLLM:
    def __init__(self):
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "35"))
        self.default_provider = os.getenv("LLM_PROVIDER", "auto").lower()
        self.last_provider = "fallback"
        self.last_model = "none"

    def _openai(self, model: str):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def _gemini(self, model: str):
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            google_api_key=os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY"),
        )

    def _deepseek(self, model: str):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv(
                "DEEPSEEK_BASE_URL",
                "https://api.deepseek.com"
            ),
        )

    def _ollama(self, model: str):
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model,
            temperature=self.temperature,
            base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434"
            ),
        )

    def available_providers(self):
        providers = []

        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")

        if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            providers.append("gemini")

        if os.getenv("DEEPSEEK_API_KEY"):
            providers.append("deepseek")

        providers.append("ollama")

        return providers

    def route(self, prompt: str, task: str = "general") -> tuple[str, str]:
        requested = os.getenv(
            f"{task.upper()}_LLM_PROVIDER",
            self.default_provider
        ).lower()

        if requested != "auto":
            provider = requested

        elif task in {"evaluator", "reviewer"} and os.getenv("OPENAI_API_KEY"):
            provider = "openai"

        elif task in {"research", "writer"} and os.getenv("DEEPSEEK_API_KEY"):
            provider = "deepseek"

        elif task == "planner" and (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        ):
            provider = "gemini"

        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"

        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            provider = "gemini"

        elif os.getenv("DEEPSEEK_API_KEY"):
            provider = "deepseek"

        else:
            provider = "ollama"

        models = {
            "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
        }

        return provider, models.get(provider, models["ollama"])

    def invoke(self, prompt: str, task: str = "general") -> LLMResponse:
        provider, model = self.route(prompt, task)

        self.last_provider = provider
        self.last_model = model

        try:
            client_factory = {
                "openai": self._openai,
                "gemini": self._gemini,
                "deepseek": self._deepseek,
                "ollama": self._ollama,
            }[provider]

            response: Any = client_factory(model).invoke(prompt)

            content = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )

            return LLMResponse(
                content=content,
                provider=provider,
                model=model,
            )

        except Exception as exc:
            print(f"[LLM ROUTER] {provider}/{model} failed")
            traceback.print_exc()

            return LLMResponse(
                content=f"ERROR: {str(exc)}",
                provider=provider,
                model=model,
            )


llm = RoutedLLM()


def invoke_llm(prompt: str, task: str = "general") -> str:
    return llm.invoke(prompt, task=task).content


def llm_status():
    return {
        "available": llm.available_providers(),
        "selected": llm.default_provider,
        "last_provider": llm.last_provider,
        "last_model": llm.last_model,
    }