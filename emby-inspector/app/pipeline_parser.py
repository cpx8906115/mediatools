from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    urls = URL_RE.findall(text)
    # strip trailing punctuation + de-dup while preserving order
    seen = set()
    cleaned = []
    for u in urls:
        cu = u.strip().rstrip(")]}>,.;。！，！")
        if cu in seen:
            continue
        seen.add(cu)
        cleaned.append(cu)
    return cleaned


def classify_link(url: str) -> tuple[str, dict] | None:
    """Return (provider, info) where provider in {"123","115","quark"}."""
    try:
        p = urlparse(url)
    except Exception:
        return None

    host = (p.netloc or "").lower()
    qs = parse_qs(p.query or "")

    def q1(name: str) -> str | None:
        v = qs.get(name)
        if not v:
            return None
        return v[0]

    # 123 variants
    if any(h in host for h in ["123912.com", "123pan.com", "123684.com", "123865.com", "123952.com"]):
        info = {"url": url}
        pwd = q1("pwd") or q1("password")
        if pwd:
            info["pwd"] = pwd
        return "123", info

    # 115 variants
    if any(h in host for h in ["115cdn.com", "115.com"]):
        info = {"url": url}
        pwd = q1("password") or q1("pwd")
        if pwd:
            info["password"] = pwd
        return "115", info

    # Quark share
    if any(h in host for h in ["pan.quark.cn", "quark.cn"]):
        info = {"url": url}
        pwd = q1("pwd") or q1("password")
        if pwd:
            info["pwd"] = pwd
        # extract share id from path: /s/<id>
        parts = [p for p in (p.path or "").split("/") if p]
        if len(parts) >= 2 and parts[0] == "s":
            info["share_id"] = parts[1]
        # preserve fragment (quark uses #/list/share)
        if p.fragment:
            info["fragment"] = p.fragment
        return "quark", info

    return None


TMDB_RE = re.compile(r"TMDB\s*ID\s*[:：]\s*(\d+)", re.IGNORECASE)
SE_RE = re.compile(r"S(\d{1,2})E(\d{1,3})", re.IGNORECASE)


def parse_media_block(text: str) -> dict:
    """Heuristic parse for the media description blocks seen in TG."""
    out: dict = {}
    if not text:
        return out

    m = TMDB_RE.search(text)
    if m:
        out["tmdb_id"] = int(m.group(1))

    m2 = SE_RE.search(text)
    if m2:
        out["season"] = int(m2.group(1))
        out["episode"] = int(m2.group(2))

    # title: line like "📺 电视剧：xxx" or "电影：xxx"
    for line in text.splitlines():
        line = line.strip()
        if "：" in line and ("电视剧" in line or "电影" in line):
            try:
                left, right = line.split("：", 1)
                out["title"] = right.strip()
                if "电视剧" in left:
                    out["media_type"] = "series"
                elif "电影" in left:
                    out["media_type"] = "movie"
            except Exception:
                pass
        if line.startswith("#"):
            tags = out.setdefault("tags", [])
            tags.append(line.lstrip("#").strip())

    return out
