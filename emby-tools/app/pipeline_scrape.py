from __future__ import annotations

import re
from dataclasses import dataclass

from .pipeline_parser import extract_urls, classify_link
from .tmdb_client import TMDBClient
from .genre_map import map_genres_to_category


TITLE_CLEAN_RE = re.compile(r"(\b(2160p|1080p|720p|4k|web[-\s]?dl|bluray|bdrip|hdr|dv)\b|\[.*?\]|\(.*?\))", re.IGNORECASE)
SE_RE = re.compile(r"S(\d{1,2})E(\d{1,3})", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


@dataclass
class ScrapeResult:
    provider: str
    link_info: dict
    query: str
    year: int | None
    season: int | None
    episode: int | None
    quality: str | None


def _guess_quality(text: str) -> str | None:
    tl = (text or "").lower()
    if "2160" in tl or "4k" in tl:
        return "2160p"
    if "1080" in tl:
        return "1080p"
    if "720" in tl:
        return "720p"
    return None


def guess_from_text(text: str) -> ScrapeResult | None:
    urls = extract_urls(text or "")
    if not urls:
        return None

    for u in urls:
        c = classify_link(u)
        if not c:
            continue
        provider, info = c

        # crude query guess: use url host+path as fallback
        query = text.strip().splitlines()[0].strip() if text.strip() else provider
        query = TITLE_CLEAN_RE.sub(" ", query)
        query = re.sub(r"\s+", " ", query).strip()
        if len(query) < 2:
            query = provider

        y = None
        ym = YEAR_RE.search(text)
        if ym:
            try:
                y = int(ym.group(1))
            except Exception:
                y = None

        s = e = None
        sm = SE_RE.search(text)
        if sm:
            s = int(sm.group(1))
            e = int(sm.group(2))

        q = _guess_quality(text)

        return ScrapeResult(provider=provider, link_info=info, query=query, year=y, season=s, episode=e, quality=q)

    return None


async def tmdb_match_tv(query: str, year: int | None = None) -> dict | None:
    """Return best matched tv show details (zh-CN)."""
    cli = TMDBClient(language="zh-CN")
    data = await cli.search_tv(query=query, year=year)
    results = data.get("results") or []
    if not results:
        return None

    # default: first result (TMDB already sorts by relevance/popularity)
    best = results[0]
    tmdb_id = best.get("id")
    if not tmdb_id:
        return None

    details = await cli.tv_details(int(tmdb_id))
    return details


def tmdb_category(details: dict) -> str:
    genres = []
    for g in (details or {}).get("genres") or []:
        name = g.get("name")
        if name:
            genres.append(name)
    return map_genres_to_category(genres)
