from __future__ import annotations

from pycon_agent.data import Talk


def _talk_to_dict(talk: Talk) -> dict:
    return {
        "title": talk.title,
        "speaker": talk.speaker,
        "track": talk.track,
        "date": talk.date,
        "start": talk.start,
        "room": talk.room,
        "abstract": talk.abstract,
    }


def search_talks(query: str, talks: list[Talk]) -> list[dict]:
    """Search talks by keyword across titles, abstracts, speakers, and tracks."""
    query_lower = query.lower()
    terms = query_lower.split()

    scored: list[tuple[int, Talk]] = []
    for talk in talks:
        searchable = " ".join(filter(None, [
            talk.title.lower(),
            (talk.abstract or "").lower(),
            talk.speaker.lower(),
            (talk.track or "").lower(),
        ]))
        score = sum(1 for term in terms if term in searchable)
        if score > 0:
            scored.append((score, talk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [_talk_to_dict(talk) for _, talk in scored[:10]]


def recommend_talks(profile: str, talks: list[Talk]) -> list[dict]:
    """Return all talks with titles, speakers, and tracks so the LLM can reason about relevance.

    Abstracts are truncated to keep total token count manageable (~8K tokens for ~100 talks).
    The agent (LLM) will select and rank the most relevant ones.
    """
    results = []
    for talk in talks:
        d = _talk_to_dict(talk)
        if d.get("abstract"):
            d["abstract"] = d["abstract"][:100]
        results.append(d)
    return results


def find_related(talk_title: str, talks: list[Talk]) -> list[dict]:
    """Find talks related to a given talk by track and keyword overlap."""
    target = None
    for talk in talks:
        if talk.title.lower() == talk_title.lower():
            target = talk
            break

    if target is None:
        for talk in talks:
            if talk_title.lower() in talk.title.lower():
                target = talk
                break

    if target is None:
        return []

    title_words = set(target.title.lower().split()) - {
        "the", "a", "an", "of", "in", "for", "and", "or", "to", "with", "from", "on", "is", "how", "your", "by",
    }
    abstract_words = set()
    if target.abstract:
        abstract_words = set(target.abstract.lower().split()[:50]) - {
            "the", "a", "an", "of", "in", "for", "and", "or", "to", "with", "from", "on", "is", "it", "that", "this",
        }

    key_words = title_words | abstract_words

    scored: list[tuple[float, Talk]] = []
    for talk in talks:
        if talk.title == target.title:
            continue

        score = 0.0
        if talk.track and target.track and talk.track == target.track:
            score += 3.0

        talk_words = set(talk.title.lower().split())
        if talk.abstract:
            talk_words |= set(talk.abstract.lower().split()[:50])

        overlap = len(key_words & talk_words)
        score += overlap * 0.5

        if score > 0:
            scored.append((score, talk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [_talk_to_dict(talk) for _, talk in scored[:10]]
