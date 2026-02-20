"""LLM provider abstraction for Ollama, OpenAI, and OpenRouter."""

from abc import ABC, abstractmethod
import ollama
import openai


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> str:
        """Send messages to LLM and return text response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier string
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Response text from the LLM

        Raises:
            Exception: Provider-specific errors (network, API, etc.)
        """
        ...


class OllamaProvider(LLMProvider):
    """Synchronous Ollama provider for local LLM inference."""

    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama provider.

        Args:
            host: Ollama server URL
        """
        self.host = host

    def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> str:
        """Send messages to Ollama and return text response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model name (e.g., "qwen2.5:7b-instruct")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response text from Ollama

        Raises:
            ollama.ResponseError: API errors
            requests.RequestException: Network errors
        """
        client = ollama.Client(host=self.host)
        response = client.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        return response["message"]["content"]


class OpenAIProvider(LLMProvider):
    """Synchronous OpenAI-compatible provider (OpenAI API, Azure, or custom base URL)."""

    def __init__(
        self, api_key: str, base_url: str = "https://api.openai.com/v1"
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: API key (OPENAI_API_KEY for OpenAI or compatible endpoints)
            base_url: API base URL (default: https://api.openai.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url

    def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> str:
        """Send messages to OpenAI (or compatible API) and return text response."""
        client = openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class OpenRouterProvider(LLMProvider):
    """Synchronous OpenRouter provider for cloud LLM inference."""

    def __init__(
        self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"
    ):
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key
        self.base_url = base_url

    def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> str:
        """Send messages to OpenRouter and return text response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier (e.g., "qwen/qwen2.5-coder-7b-instruct")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response text from OpenRouter

        Raises:
            openai.APIError: API errors
            openai.APIConnectionError: Network errors
        """
        client = openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
