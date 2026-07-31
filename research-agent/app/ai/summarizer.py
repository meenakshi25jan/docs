"""AI summarization with OpenAI, Ollama, and local LLM support."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Any

import aiohttp

from app.utils.helpers import truncate_text
from app.utils.logger import get_logger
from config import Settings, get_settings

logger = get_logger()

SUMMARY_PROMPT = """You are a research analyst. Analyze the following web research data about "{query}".

Sources ({source_count} pages):
{context}

Provide a structured research summary in JSON with these keys:
- executive_summary: 2-3 paragraph overview
- findings: list of key findings with citations like [1], [2]
- timeline: list of chronological events if applicable, else empty list
- key_facts: list of important facts
- statistics: list of numeric statistics found
- references: list of objects with title, url, and citation_number
- confidence_score: float 0.0-1.0 based on source quality and consistency
- source_urls: list of all source URLs

Return ONLY valid JSON."""


@dataclass
class ResearchSummary:
    """Structured research summary output."""

    executive_summary: str = ""
    findings: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    key_facts: list[str] = field(default_factory=list)
    statistics: list[str] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.5
    source_urls: list[str] = field(default_factory=list)
    raw_response: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "executive_summary": self.executive_summary,
            "findings": self.findings,
            "timeline": self.timeline,
            "key_facts": self.key_facts,
            "statistics": self.statistics,
            "references": self.references,
            "confidence_score": self.confidence_score,
            "source_urls": self.source_urls,
        }


class Summarizer:
    """Generate AI-powered research summaries."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def summarize(
        self,
        query: str,
        pages: list[Any],
        semantic_context: list[dict[str, Any]] | None = None,
    ) -> ResearchSummary:
        """Summarize crawled pages using configured LLM provider."""
        context = self._build_context(pages, semantic_context)
        if self.settings.llm_provider == "none":
            return self._fallback_summary(query, pages)

        prompt = SUMMARY_PROMPT.format(
            query=query,
            source_count=len(pages),
            context=context,
        )

        try:
            if self.settings.llm_provider == "openai":
                raw = await self._call_openai(prompt)
            elif self.settings.llm_provider == "ollama":
                raw = await self._call_ollama(prompt)
            elif self.settings.llm_provider == "local":
                raw = await self._call_local_llm(prompt)
            else:
                return self._fallback_summary(query, pages)

            return self._parse_summary(raw, pages)
        except Exception as exc:
            logger.error("Summarization failed: {}", exc)
            return self._fallback_summary(query, pages)

    def _build_context(
        self,
        pages: list[Any],
        semantic_context: list[dict[str, Any]] | None,
    ) -> str:
        parts: list[str] = []
        for i, page in enumerate(pages[:30], start=1):
            title = page.title or "Untitled"
            text = truncate_text(page.visible_text or "", 1500)
            parts.append(f"[{i}] {title}\nURL: {page.url}\n{text}\n")

        if semantic_context:
            parts.append("\nRelevant semantic matches:")
            for item in semantic_context[:5]:
                parts.append(
                    f"- {item.get('title', '')} ({item.get('url', '')}): "
                    f"{truncate_text(item.get('text', ''), 300)}"
                )
        return "\n".join(parts)

    async def _call_openai(self, prompt: str) -> str:
        if not self.settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        base_url = self.settings.openai_base_url or "https://api.openai.com/v1"
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": "You are a research analyst. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]

    async def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=180),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("response", "{}")

    async def _call_local_llm(self, prompt: str) -> str:
        if not self.settings.local_llm_url:
            raise ValueError("Local LLM URL not configured")

        payload = {
            "model": self.settings.local_llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.settings.local_llm_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=180),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                return data.get("response", "{}")

    def _parse_summary(self, raw: str, pages: list[Any]) -> ResearchSummary:
        try:
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(json_match.group() if json_match else raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON, using fallback")
            return self._fallback_summary("", pages)

        return ResearchSummary(
            executive_summary=data.get("executive_summary", ""),
            findings=data.get("findings", []),
            timeline=data.get("timeline", []),
            key_facts=data.get("key_facts", []),
            statistics=data.get("statistics", []),
            references=data.get("references", []),
            confidence_score=float(data.get("confidence_score", 0.5)),
            source_urls=data.get("source_urls", [p.url for p in pages]),
            raw_response=raw,
        )

    def _fallback_summary(self, query: str, pages: list[Any]) -> ResearchSummary:
        """Generate a heuristic summary without LLM."""
        findings: list[str] = []
        key_facts: list[str] = []
        statistics: list[str] = []
        references: list[dict[str, Any]] = []

        for i, page in enumerate(pages[:20], start=1):
            title = page.title or page.url
            references.append(
                {"title": title, "url": page.url, "citation_number": i}
            )
            if page.h1:
                findings.append(f"[{i}] {page.h1[0]}")
            if page.paragraphs:
                key_facts.append(f"[{i}] {truncate_text(page.paragraphs[0], 200)}")

            stat_pattern = re.findall(r"\b\d+(?:\.\d+)?%?\b", page.visible_text or "")
            statistics.extend(stat_pattern[:3])

        successful = sum(1 for p in pages if p.visible_text)
        confidence = min(0.9, 0.3 + (successful / max(len(pages), 1)) * 0.6)

        executive = (
            f"Research on '{query}' collected {len(pages)} pages "
            f"with {successful} containing extractable content. "
            f"Key themes emerge from {len(findings)} primary headings across sources."
        )

        return ResearchSummary(
            executive_summary=executive,
            findings=findings[:15],
            timeline=[],
            key_facts=key_facts[:15],
            statistics=list(dict.fromkeys(statistics))[:20],
            references=references,
            confidence_score=round(confidence, 2),
            source_urls=[p.url for p in pages],
        )
