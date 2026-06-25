import math

from tavily import TavilyClient

from app.config import settings
from app.models.document import Document
from app.services.chatbot_algorithm_service import (
    extract_keywords_by_tfidf,
    normalize_text,
)


TRUSTED_SOURCE_KEYWORDS = {
    "docs.python.org": 1.0,
    "fastapi.tiangolo.com": 1.0,
    "developer.mozilla.org": 1.0,
    "learn.microsoft.com": 0.95,
    "w3schools.com": 0.85,
    "geeksforgeeks.org": 0.8,
    "tutorialspoint.com": 0.75,
    "realpython.com": 0.9,
    "freecodecamp.org": 0.85,
    "coursera.org": 0.7,
    "edx.org": 0.7,
}


def build_existing_context(
    subject_name: str,
    documents: list[Document],
) -> str:
    document_text = "\n".join(
        [
            f"{document.title}\n{document.content[:1200]}"
            for document in documents
            if document.content
        ]
    )

    return f"{subject_name}\n{document_text}".strip()


def build_search_query(
    subject_name: str,
    topic: str,
    documents: list[Document],
) -> tuple[str, list[str]]:
    context = build_existing_context(subject_name, documents)

    keywords = extract_keywords_by_tfidf(
        texts=[context] if context else [topic],
        top_n=8,
    )

    clean_keywords = [
        keyword
        for keyword in keywords
        if len(keyword.split()) <= 3
    ]

    query_parts = [subject_name, topic] + clean_keywords[:5]

    query = " ".join(
        [
            part
            for part in query_parts
            if part and part.strip()
        ]
    )

    return query.strip(), clean_keywords


async def call_google_search_api(
    query: str,
    max_results: int = 5,
) -> list[dict]:
    """
    Giữ nguyên tên hàm để không cần sửa router chatbot.
    Bên trong đã đổi sang Tavily Search.
    """
    if not settings.tavily_api_key:
        raise ValueError("Chưa cấu hình TAVILY_API_KEY trong file .env.")

    client = TavilyClient(api_key=settings.tavily_api_key)

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
        include_answer=False,
        include_raw_content=False,
    )

    results = response.get("results", [])

    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("content", ""),
            "link": item.get("url", ""),
            "displayLink": extract_domain(item.get("url", "")),
        }
        for item in results
    ]


def extract_domain(url: str) -> str:
    if not url:
        return ""

    cleaned_url = (
        url.replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
    )

    return cleaned_url.split("/")[0]


def calculate_keyword_overlap(
    keywords: list[str],
    candidate_text: str,
) -> tuple[float, list[str]]:
    if not keywords:
        return 0.0, []

    normalized_candidate = normalize_text(candidate_text)

    matched_keywords = [
        keyword
        for keyword in keywords
        if keyword.lower() in normalized_candidate
    ]

    score = len(matched_keywords) / max(len(keywords), 1)

    return float(score), matched_keywords


def calculate_source_score(display_link: str | None) -> float:
    if not display_link:
        return 0.5

    domain = display_link.lower()

    for source, score in TRUSTED_SOURCE_KEYWORDS.items():
        if source in domain:
            return score

    if domain.endswith(".edu"):
        return 0.85

    if domain.endswith(".org"):
        return 0.7

    return 0.55


def calculate_title_match(
    topic: str,
    title: str,
) -> float:
    topic_words = set(normalize_text(topic).split())
    title_words = set(normalize_text(title).split())

    if not topic_words:
        return 0.0

    matched = topic_words.intersection(title_words)

    return len(matched) / max(len(topic_words), 1)


def rank_search_results(
    subject_name: str,
    topic: str,
    documents: list[Document],
    search_items: list[dict],
    keywords: list[str],
) -> list[dict]:
    ranked_results: list[dict] = []

    for item in search_items:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        link = item.get("link", "").strip()
        display_link = item.get("displayLink", "").strip()

        candidate_text = f"{title}\n{snippet}\n{display_link}"

        keyword_overlap, matched_keywords = calculate_keyword_overlap(
            keywords=keywords,
            candidate_text=candidate_text,
        )

        source_score = calculate_source_score(display_link)
        title_match = calculate_title_match(topic, title)

        final_score = (
            0.45 * keyword_overlap
            + 0.30 * source_score
            + 0.25 * title_match
        )

        final_score_percent = round(final_score * 100, 2)

        if math.isnan(final_score_percent):
            final_score_percent = 0.0

        ranked_results.append(
            {
                "title": title,
                "snippet": snippet,
                "link": link,
                "display_link": display_link,
                "relevance_score": final_score_percent,
                "matched_keywords": matched_keywords[:8],
            }
        )

    ranked_results.sort(
        key=lambda result: result["relevance_score"],
        reverse=True,
    )

    return ranked_results