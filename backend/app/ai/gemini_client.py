import json
import logging
import os
import re
from typing import Any, Dict, Iterator, Optional
from app.config import settings

logger = logging.getLogger("resume_ai")


class GeminiClient:
    """
    Dedicated Google Gemini API client supporting:
    1. Modern official google.genai SDK (v1+)
    2. Legacy google.generativeai SDK (v0.3+)
    3. Direct HTTPS REST API fallback
    4. Text generation, JSON extraction, and token streaming
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", "")
            or os.getenv("GEMINI_API_KEY", "")
            or getattr(settings, "LLM_API_KEY", "")
            or os.getenv("LLM_API_KEY", "")
        )
        self.model_name = (
            model_name
            or getattr(settings, "GEMINI_MODEL", "")
            or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        )
        self.client_type = None
        self.client = None
        self.model = None
        self.available = False

        if not self.api_key:
            logger.info("GEMINI_API_KEY not configured. Intelligent fallback will be utilized.")
            return

        # 1. Try modern official google.genai SDK
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.client_type = "google.genai"
            self.available = True
            logger.info(f"Initialized Gemini Client via google.genai with model {self.model_name}")
            return
        except Exception as e:
            logger.debug(f"google.genai initialization skipped/failed: {e}")

        # 2. Try legacy google.generativeai SDK
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            self.model = legacy_genai.GenerativeModel(self.model_name)
            self.client_type = "google.generativeai"
            self.available = True
            logger.info(f"Initialized Gemini Client via google.generativeai with model {self.model_name}")
            return
        except Exception as e:
            logger.debug(f"google.generativeai initialization skipped/failed: {e}")

        # 3. Direct REST API fallback
        if self.api_key:
            self.client_type = "rest"
            self.available = True
            logger.info("Initialized Gemini Client via direct REST API fallback")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response text from Gemini API."""
        if not self.available:
            raise RuntimeError("Gemini API is not configured or unavailable.")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        if self.client_type == "google.genai":
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text or ""

        elif self.client_type == "google.generativeai":
            response = self.model.generate_content(full_prompt)
            return response.text or ""

        elif self.client_type == "rest":
            return self._call_rest_api(full_prompt)

        raise RuntimeError("No active Gemini client provider.")

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate and parse structured JSON from Gemini API."""
        json_instruction = "\n\nCRITICAL: Return ONLY valid JSON. Do not include markdown code block backticks."
        p = prompt + json_instruction
        raw = self.generate_text(p, system_prompt=system_prompt)
        return self._extract_json(raw)

    def stream_text(self, prompt: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """Stream chunks of response text from Gemini API."""
        if not self.available:
            raise RuntimeError("Gemini API is not configured or unavailable.")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        if self.client_type == "google.genai":
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=full_prompt
            )
            for chunk in response_stream:
                text = getattr(chunk, "text", "")
                if text:
                    yield text

        elif self.client_type == "google.generativeai":
            response_stream = self.model.generate_content(full_prompt, stream=True)
            for chunk in response_stream:
                text = getattr(chunk, "text", "")
                if text:
                    yield text

        else:
            # REST or fallback
            yield self.generate_text(full_prompt)

    def _call_rest_api(self, prompt: str) -> str:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        if not text:
            return {}
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback regex extraction for { ... }
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise


_gemini_client_instance: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client_instance
    if _gemini_client_instance is None:
        _gemini_client_instance = GeminiClient()
    return _gemini_client_instance
