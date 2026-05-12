"""Input guardrails for Lab 24.

This module is intentionally offline-first so the lab can be demonstrated
without paid APIs. The classes keep the same shape as a Presidio/topic guard
stack, so the regex layer can be replaced with Presidio or embeddings later.
"""

from __future__ import annotations

import asyncio
import base64
import re
import time
from dataclasses import dataclass
from typing import Iterable


VN_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "CCCD": re.compile(r"\b\d{12}\b"),
    "PHONE_VN": re.compile(r"\b(?:\+84|0)(?:\d[\s.-]?){8,10}\d\b"),
    "TAX_CODE": re.compile(r"\b\d{10}(?:-\d{3})?\b"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
}

EN_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "PHONE": re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ADDRESS": re.compile(r"\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:Street|St|Road|Rd|Avenue|Ave)\b"),
    "PERSON": re.compile(r"\b(?:John Smith|Nguyen Van A|Nguyen Van B|Ly Van Binh)\b", re.IGNORECASE),
}


INJECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "ignore_instructions": re.compile(r"ignore (?:all )?(?:previous|prior|system)? ?instructions", re.IGNORECASE),
    "dan": re.compile(r"\b(?:DAN|JailBreak|developer mode|no restrictions)\b", re.IGNORECASE),
    "roleplay_evil": re.compile(r"\b(?:evil AI|no guidelines|bypass policy|simulate illegal)\b", re.IGNORECASE),
    "exfiltration": re.compile(r"\b(?:reveal|print|show).{0,30}(?:system prompt|hidden prompt|secret)\b", re.IGNORECASE),
    "harmful": re.compile(r"\b(?:hack|malware|phishing|steal credentials|make a bomb)\b", re.IGNORECASE),
    "encoded": re.compile(r"\b(?:base64|rot13|hex encoded|decode this)\b", re.IGNORECASE),
}


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reason: str
    latency_ms: float


class InputGuard:
    """PII redaction plus prompt-injection detection."""

    def scrub_regex(self, text: str) -> tuple[str, set[str]]:
        found: set[str] = set()
        output = text or ""
        for label, pattern in {**VN_PII_PATTERNS, **EN_PII_PATTERNS}.items():
            if pattern.search(output):
                found.add(label)
                output = pattern.sub(f"[{label}]", output)
        return output, found

    def sanitize(self, text: str) -> tuple[str, float, set[str]]:
        start = time.perf_counter()
        output, found = self.scrub_regex(text)
        latency_ms = (time.perf_counter() - start) * 1000
        return output, latency_ms, found

    async def sanitize_async(self, text: str) -> tuple[str, float, set[str]]:
        return await asyncio.to_thread(self.sanitize, text)


class InjectionGuard:
    """Rule-based jailbreak and prompt-injection detector."""

    def check(self, text: str) -> GuardResult:
        start = time.perf_counter()
        normalized = text or ""
        decoded_hits = self._decoded_hits(normalized)
        for label, pattern in INJECTION_PATTERNS.items():
            if pattern.search(normalized):
                return GuardResult(False, f"Blocked prompt injection: {label}", self._elapsed(start))
        if decoded_hits:
            return GuardResult(False, f"Blocked encoded injection: {decoded_hits}", self._elapsed(start))
        return GuardResult(True, "No injection indicators found", self._elapsed(start))

    async def check_async(self, text: str) -> GuardResult:
        return await asyncio.to_thread(self.check, text)

    @staticmethod
    def _elapsed(start: float) -> float:
        return (time.perf_counter() - start) * 1000

    @staticmethod
    def _decoded_hits(text: str) -> str:
        tokens = re.findall(r"[A-Za-z0-9+/=]{12,}", text)
        for token in tokens:
            try:
                decoded = base64.b64decode(token, validate=True).decode("utf-8", errors="ignore")
            except Exception:
                continue
            if "ignore" in decoded.lower() or "instructions" in decoded.lower():
                return decoded[:60]
        return ""


class TopicGuard:
    """Lightweight lexical topic validator.

    Allowed topics are intentionally tailored to the Lab 24 domain.
    """

    def __init__(self, allowed_topics: Iterable[str] | None = None) -> None:
        topics = list(allowed_topics or [
            "rag evaluation",
            "ragas metrics",
            "llm judge calibration",
            "guardrails safety",
            "pii redaction",
            "latency monitoring",
            "vinuniversity ai lab",
        ])
        self.topic_terms = {
            topic: set(re.findall(r"[a-z0-9]+", topic.lower()))
            for topic in topics
        }
        self.domain_terms = {
            "rag", "ragas", "retrieval", "context", "faithfulness", "answer",
            "relevancy", "precision", "recall", "judge", "kappa", "guardrail",
            "pii", "redaction", "llama", "latency", "eval", "evaluation",
            "monitoring", "prompt", "injection", "vinuniversity", "lab",
            "alert", "playbook", "position", "bias", "pairwise", "adversarial",
            "testing",
        }

    def check(self, text: str) -> tuple[bool, str]:
        tokens = set(re.findall(r"[a-z0-9]+", (text or "").lower()))
        if not tokens:
            return False, "Please ask a question about RAG evaluation or guardrails."

        domain_overlap = tokens & self.domain_terms
        best_topic = "rag evaluation"
        best_score = 0.0
        for topic, terms in self.topic_terms.items():
            score = len(tokens & terms) / max(1, len(terms))
            if score > best_score:
                best_score = score
                best_topic = topic

        if domain_overlap or best_score >= 0.34:
            return True, f"On topic: {best_topic}"
        return False, f"I can help with Lab 24 RAG evaluation, judging, guardrails, and monitoring. Closest topic: {best_topic}."

    async def check_async(self, text: str) -> tuple[bool, str]:
        return await asyncio.to_thread(self.check, text)


def refuse_response(reason: str) -> str:
    return f"I cannot process that request as written. {reason}"
