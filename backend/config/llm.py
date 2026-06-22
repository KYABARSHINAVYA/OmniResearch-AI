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
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "900"))
        self.enable_fallback = os.getenv("LLM_ENABLE_FALLBACK", "true").lower() == "true"
        self.default_provider = os.getenv("LLM_PROVIDER", "auto").lower()
        self.last_provider = "fallback"
        self.last_model = "none"
        self.last_error = ""

    def _openai(self, model: str):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            max_tokens=self.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def _gemini(self, model: str):
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            max_output_tokens=self.max_tokens,
            google_api_key=os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY"),
        )

    def _deepseek(self, model: str):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=self.temperature,
            timeout=self.timeout,
            max_tokens=self.max_tokens,
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
            num_predict=self.max_tokens,
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

        if os.getenv("OLLAMA_ENABLED", "true").lower() == "true":
            providers.append("ollama")

        return providers

    def _models(self):
        return {
            "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
        }

    def route(self, prompt: str, task: str = "general") -> tuple[str, str]:
        requested = os.getenv(
            f"{task.upper()}_LLM_PROVIDER",
            self.default_provider
        ).lower()

        if requested != "auto":
            provider = requested

        elif task in {"evaluator", "reviewer"} and (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        ):
            provider = "gemini"

        elif task in {"evaluator", "reviewer"} and os.getenv("OPENAI_API_KEY"):
            provider = "openai"

        elif task in {"research", "writer"} and os.getenv("DEEPSEEK_API_KEY"):
            provider = "deepseek"

        elif task == "planner" and (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        ):
            provider = "gemini"

        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            provider = "gemini"

        elif os.getenv("DEEPSEEK_API_KEY"):
            provider = "deepseek"

        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"

        else:
            provider = "ollama"

        models = self._models()

        return provider, models.get(provider, models["ollama"])

    def _fallback_order(self, first_provider: str) -> list[str]:
        available = self.available_providers()
        if not self.enable_fallback:
            return [first_provider] if first_provider in available else available[:1]

        preferred = [first_provider, "gemini", "deepseek", "openai", "ollama"]
        ordered = []

        for provider in preferred:
            if provider in available and provider not in ordered:
                ordered.append(provider)

        return ordered or ["ollama"]

    def _is_quota_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return (
            "insufficient_quota" in message
            or "exceeded your current quota" in message
            or "error code: 429" in message
        )

    def invoke(self, prompt: str, task: str = "general") -> LLMResponse:
        provider, model = self.route(prompt, task)
        models = self._models()

        for candidate_provider in self._fallback_order(provider):
            candidate_model = models.get(candidate_provider, models["ollama"])
            self.last_provider = candidate_provider
            self.last_model = candidate_model
            self.last_error = ""

            try:
                client_factory = {
                    "openai": self._openai,
                    "gemini": self._gemini,
                    "deepseek": self._deepseek,
                    "ollama": self._ollama,
                }[candidate_provider]

                response: Any = client_factory(candidate_model).invoke(prompt)

                content = (
                    response.content
                    if hasattr(response, "content")
                    else str(response)
                )

                return LLMResponse(
                    content=content,
                    provider=candidate_provider,
                    model=candidate_model,
                )

            except Exception as exc:
                reason = "quota" if self._is_quota_error(exc) else "error"
                self.last_error = f"{candidate_provider}/{candidate_model} failed ({reason}): {exc}"
                print(f"[LLM ROUTER] {candidate_provider}/{candidate_model} failed ({reason})")
                traceback.print_exc()

        return LLMResponse(
            content=(
                "I could not reach any configured language model. "
                "Please check your LLM provider keys, quota, and local Ollama status."
            ),
            provider="fallback",
            model="none",
        )


llm = RoutedLLM()


def invoke_llm(prompt: str, task: str = "general") -> str:
    return llm.invoke(prompt, task=task).content


def llm_status():
    return {
        "available": llm.available_providers(),
        "selected": llm.default_provider,
        "fallback_enabled": llm.enable_fallback,
        "last_provider": llm.last_provider,
        "last_model": llm.last_model,
        "last_error": llm.last_error,
    }
