from dataclasses import dataclass

from app.config import get_settings
from app.utils.text import compact_text, simple_keywords


@dataclass
class AIAnalysisResult:
    summary: str
    keywords: list[str]
    sentiment: str
    category: str
    trend_opinion: str


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def analyze_text(self, title: str | None, text: str | None) -> AIAnalysisResult:
        source = compact_text(" ".join(part for part in [title, text] if part), limit=1600)
        keywords = simple_keywords(source)
        provider_ready = self.settings.ai_provider != "mock" and bool(self.settings.ai_api_key)
        if not provider_ready:
            return AIAnalysisResult(
                summary=compact_text(source, limit=220) or "No readable public text was extracted.",
                keywords=keywords,
                sentiment="neutral",
                category=self._guess_category(source),
                trend_opinion="Local fallback analysis. Configure AI_PROVIDER and AI_API_KEY for model-generated insight.",
            )
        return AIAnalysisResult(
            summary=compact_text(source, limit=220),
            keywords=keywords,
            sentiment="neutral",
            category=self._guess_category(source),
            trend_opinion=f"Provider '{self.settings.ai_provider}' is configured; plug vendor SDK call here.",
        )

    def summarize_daily(self, titles: list[str]) -> dict[str, object]:
        combined = compact_text(" ".join(titles), limit=2000)
        return {
            "summary": compact_text(combined, limit=260) or "No hotspots captured for this date.",
            "keywords": simple_keywords(combined, limit=12),
            "sentiment_overview": "neutral",
            "trend_opinion": "Topics with repeated platform presence deserve continued monitoring.",
            "platform_comparison": "Compare counts, repeated keywords, and rank movement by platform.",
            "content_suggestions": "Create explainers, timeline posts, and cross-platform comparison reports.",
        }

    def _guess_category(self, text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["github", "ai", "model", "software", "tech"]):
            return "technology"
        if any(word in lowered for word in ["market", "finance", "stock"]):
            return "finance"
        return "general"
