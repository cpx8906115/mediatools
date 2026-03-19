from __future__ import annotations

# Very small starter mapping. Can be extended later.


def map_genres_to_category(genres: list[str]) -> str:
    g = {x.strip().lower() for x in genres if x and x.strip()}

    # animation first
    if "animation" in g or "动画" in g:
        return "动漫"

    if "documentary" in g or "纪录片" in g:
        return "纪录片"

    if "reality" in g or "真人秀" in g:
        return "综艺"

    if "sci-fi & fantasy" in g or "science fiction" in g or "fantasy" in g or "科幻" in g or "奇幻" in g:
        return "科幻"

    if "crime" in g or "犯罪" in g:
        return "犯罪"

    if "mystery" in g or "悬疑" in g:
        return "悬疑"

    if "action & adventure" in g or "action" in g or "adventure" in g or "动作" in g or "冒险" in g:
        return "动作"

    if "comedy" in g or "喜剧" in g:
        return "喜剧"

    if "drama" in g or "剧情" in g:
        return "剧情"

    return "未分类"
