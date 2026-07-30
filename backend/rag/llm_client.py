"""Ollama local LLM API integration client.

Communicates with local Ollama REST API endpoints with latency tracking and error handling.
"""

import time
from typing import Any, Dict, Optional

import httpx

from backend.config.settings import get_settings
from backend.logging.logger import get_logger

logger = get_logger(__name__)


class OllamaLLMClient:
    """Async HTTP client interacting with local Ollama service."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 180.0,
    ):
        """Initialize Ollama client.

        Args:
            host: Ollama HTTP base URL override.
            model: Ollama model identifier override.
            timeout_seconds: HTTP request timeout duration in seconds.
        """
        settings = get_settings()
        self.host = (host or settings.ollama_host).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout_seconds

    async def check_health(self) -> Dict[str, Any]:
        """Verify Ollama server connection and check target model availability.

        Returns:
            Dict[str, Any]: Status dictionary containing availability booleans and info.
        """
        version_url = f"{self.host}/api/version"
        tags_url = f"{self.host}/api/tags"

        status: Dict[str, Any] = {
            "server_connected": False,
            "model_available": False,
            "model_name": self.model,
            "version": None,
            "details": "",
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(version_url)
                if resp.status_code == 200:
                    status["server_connected"] = True
                    status["version"] = resp.json().get("version", "unknown")

                tags_resp = await client.get(tags_url)
                if tags_resp.status_code == 200:
                    models_data = tags_resp.json().get("models", [])
                    available_names = [m.get("name", "") for m in models_data]
                    # Match exact model name or base model name (e.g. llama3.2:3b)
                    if any(
                        self.model == name or self.model in name
                        for name in available_names
                    ):
                        status["model_available"] = True
                    else:
                        status[
                            "details"
                        ] = f"Model '{self.model}' not found in installed models: {available_names}"
        except Exception as err:
            logger.warning(f"Ollama health check failed: {str(err)}")
            status["details"] = f"Connection error: {str(err)}"

        return status

    async def generate_answer(
        self, prompt: str, temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Send prompt to Ollama /api/generate endpoint and return response content.

        Args:
            prompt: Structured input prompt text.
            temperature: Sampling temperature (lower = more deterministic).

        Returns:
            Dict[str, Any]: Dictionary with response text, latency_ms, and token metadata.
        """
        generate_url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
            },
        }

        logger.info(f"Sending prompt to local Ollama model '{self.model}'...")
        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(generate_url, json=payload)

                if response.status_code != 200:
                    error_msg = f"Ollama API returned HTTP status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                data = response.json()
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                answer_text = data.get("response", "").strip()
                eval_count = data.get("eval_count", 0)
                eval_duration_ns = data.get("eval_duration", 1)
                tokens_per_sec = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0

                logger.info(
                    f"Ollama response generated in {elapsed_ms:.2f}ms ({eval_count} tokens, {tokens_per_sec:.1f} tok/s).",
                    extra={"llm_latency_ms": elapsed_ms},
                )

                return {
                    "answer": answer_text,
                    "latency_ms": round(elapsed_ms, 2),
                    "eval_count": eval_count,
                    "tokens_per_second": round(tokens_per_sec, 2),
                }

        except httpx.ConnectError as err:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            error_detail = (
                f"Cannot connect to Ollama server at '{self.host}'. "
                f"Please ensure Ollama is running (`ollama serve`). Details: {str(err)}"
            )
            logger.error(error_detail)
            raise RuntimeError(error_detail) from err
        except httpx.TimeoutException as err:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            error_detail = f"Ollama request timed out after {self.timeout}s."
            logger.error(error_detail)
            raise TimeoutError(error_detail) from err
        except Exception as err:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Error calling Ollama API: {str(err)}", exc_info=True)
            raise
