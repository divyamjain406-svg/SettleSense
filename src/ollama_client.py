"""
Resilient client for local Ollama REST API.
Handles local LLM inference (qwen3:4b) and dense embeddings (nomic-embed-text)
with health checks, timeout management, and diagnostic error reporting.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import List, Dict, Any, Optional, Union
import json
import time
import concurrent.futures
import requests

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_GEN_MODEL,
    OLLAMA_EMBED_MODEL,
    OLLAMA_TIMEOUT,
)

class OllamaServiceError(Exception):
    """Raised when Ollama server is unreachable or reports an error."""
    pass

class OllamaModelNotFoundError(OllamaServiceError):
    """Raised when a requested model is not installed locally."""
    pass

class OllamaTimeoutError(OllamaServiceError):
    """Raised when an Ollama API call times out."""
    pass


class OllamaClient:
    """Client for local Ollama service."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        gen_model: str = OLLAMA_GEN_MODEL,
        embed_model: str = OLLAMA_EMBED_MODEL,
        timeout: int = OLLAMA_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.gen_model = gen_model
        self.embed_model = embed_model
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """
        Queries Ollama /api/tags to verify connectivity and available models.
        Returns health status dictionary.
        """
        url = f"{self.base_url}/api/tags"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                # Normalize tags (e.g. qwen3:4b or qwen3:4b-latest)
                has_gen = any(self.gen_model in m for m in models)
                has_embed = any(self.embed_model in m for m in models)
                return {
                    "reachable": True,
                    "available_models": models,
                    "gen_model_available": has_gen,
                    "embed_model_available": has_embed,
                    "error": None,
                }
            else:
                return {
                    "reachable": False,
                    "available_models": [],
                    "gen_model_available": False,
                    "embed_model_available": False,
                    "error": f"Ollama returned HTTP status {resp.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "reachable": False,
                "available_models": [],
                "gen_model_available": False,
                "embed_model_available": False,
                "error": f"Could not connect to Ollama at {self.base_url}: {e}",
            }

    def get_embeddings(self, texts: Union[str, List[str]], model: Optional[str] = None) -> List[List[float]]:
        """
        Generates dense vector embeddings using Ollama /api/embed or /api/embeddings.
        Returns list of embedding vectors.
        """
        model = model or self.embed_model
        if isinstance(texts, str):
            input_texts = [texts]
        else:
            input_texts = list(texts)

        if not input_texts:
            return []

        # Try batch /api/embed first
        url = f"{self.base_url}/api/embed"
        payload = {"model": model, "input": input_texts}

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if "embeddings" in data:
                    return data["embeddings"]
        except requests.exceptions.RequestException:
            pass

        # Fallback to single-call /api/embeddings endpoint
        fallback_url = f"{self.base_url}/api/embeddings"
        embeddings = []
        try:
            for text in input_texts:
                resp = requests.post(fallback_url, json={"model": model, "prompt": text}, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    embeddings.append(data.get("embedding", []))
                else:
                    raise OllamaServiceError(f"Embedding failed: {resp.status_code} - {resp.text}")
            return embeddings
        except requests.exceptions.RequestException as e:
            raise OllamaServiceError(f"Failed to generate embeddings from {self.base_url}: {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        format_type: Optional[str] = "json",
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[Union[int, float]] = None,
        think: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """
        Generates text or structured JSON from local LLM via /api/chat.
        Enforces a hard client-side wall-clock deadline using ThreadPoolExecutor.
        Disables reasoning mode by default (think=False) to ensure fast, deterministic JSON generation.
        Returns dictionary with 'response', 'thinking', and 'raw'.
        """
        model = model or self.gen_model
        deadline_s = float(timeout if timeout is not None else self.timeout)
        url = f"{self.base_url}/api/chat"

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if think is not None:
            payload["think"] = think

        if format_type:
            payload["format"] = format_type

        default_options: Dict[str, Any] = {
            "temperature": 0.0,
            "top_p": 0.9,
            "num_predict": 2048,
        }
        if options:
            default_options.update(options)
        payload["options"] = default_options

        t_start = time.perf_counter()
        session = requests.Session()
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        def _do_post():
            return session.post(url, json=payload, timeout=(5.0, deadline_s))

        future = pool.submit(_do_post)
        try:
            resp = future.result(timeout=deadline_s)
            elapsed = time.perf_counter() - t_start
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("message", {})
                return {
                    "response": msg.get("content", ""),
                    "thinking": msg.get("thinking", ""),
                    "raw": data,
                    "elapsed_seconds": round(elapsed, 3),
                }
            elif resp.status_code == 404:
                raise OllamaModelNotFoundError(f"Model '{model}' not found in local Ollama repository. Run `ollama pull {model}`.")
            else:
                raise OllamaServiceError(f"Ollama chat failed ({resp.status_code}): {resp.text}")
        except concurrent.futures.TimeoutError:
            elapsed = time.perf_counter() - t_start
            session.close()
            pool.shutdown(wait=False, cancel_futures=True)
            raise OllamaTimeoutError(f"Ollama call exceeded client deadline of {deadline_s}s (elapsed: {elapsed:.2f}s)")
        except requests.exceptions.Timeout as e:
            elapsed = time.perf_counter() - t_start
            session.close()
            pool.shutdown(wait=False, cancel_futures=True)
            raise OllamaTimeoutError(f"Ollama socket timed out after {deadline_s}s (elapsed: {elapsed:.2f}s): {e}")
        except requests.exceptions.RequestException as e:
            elapsed = time.perf_counter() - t_start
            session.close()
            pool.shutdown(wait=False, cancel_futures=True)
            raise OllamaServiceError(f"Ollama generation error at {self.base_url}: {e}")
        finally:
            session.close()
            pool.shutdown(wait=False, cancel_futures=True)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        format_type: Optional[str] = "json",
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[Union[int, float]] = None,
        think: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """
        Generates text or structured JSON from local LLM via /api/chat with hard client deadline.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages=messages, format_type=format_type, model=model, options=options, timeout=timeout, think=think)


