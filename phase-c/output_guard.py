"""Output guardrail for Lab 24.

The OfflineLlamaGuard class returns Llama-Guard-style safe/unsafe decisions
without requiring GPU access. Replace it with an API-backed implementation when
GROQ_API_KEY or a self-hosted Llama Guard endpoint is available.
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass


UNSAFE_OUTPUT_PATTERNS: dict[str, re.Pattern[str]] = {
    "S1_VIOLENCE": re.compile(r"\b(?:make a bomb|weapon|kill|harm someone)\b", re.IGNORECASE),
    "S2_CYBER": re.compile(r"\b(?:steal credentials|phishing kit|malware|exploit code|bypass login)\b", re.IGNORECASE),
    "S3_PRIVACY": re.compile(r"\b(?:full credit card|private key|password is|api key is)\b", re.IGNORECASE),
    "S4_SELF_HARM": re.compile(r"\b(?:self-harm instructions|suicide method)\b", re.IGNORECASE),
    "S5_ILLEGAL": re.compile(r"\b(?:evade police|launder money|forge documents)\b", re.IGNORECASE),
}


@dataclass(frozen=True)
class OutputDecision:
    is_safe: bool
    raw_result: str
    latency_ms: float


class OfflineLlamaGuard:
    """Deterministic fallback with the same contract as a Llama Guard checker."""

    def check(self, user_input: str, agent_response: str) -> OutputDecision:
        start = time.perf_counter()
        combined = f"{user_input}\n{agent_response}"
        for category, pattern in UNSAFE_OUTPUT_PATTERNS.items():
            if pattern.search(combined):
                latency_ms = (time.perf_counter() - start) * 1000
                return OutputDecision(False, f"unsafe\n{category}", latency_ms)
        latency_ms = (time.perf_counter() - start) * 1000
        return OutputDecision(True, "safe", latency_ms)

    async def check_async(self, user_input: str, agent_response: str) -> OutputDecision:
        return await asyncio.to_thread(self.check, user_input, agent_response)
