from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import httpx
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from rich.console import Console
from rich.markdown import Markdown

from pycon_agent.data import Talk, load_schedule
from pycon_agent.tools import (
    find_related as _find_related,
    recommend_talks as _recommend_talks,
    search_talks as _search_talks,
)

SCHEDULE_PATH = Path(__file__).parent.parent.parent / "schedule.json"
console = Console()

_talks: list[Talk] = []


def _get_talks() -> list[Talk]:
    global _talks
    if not _talks:
        _talks = load_schedule(SCHEDULE_PATH)
    return _talks


@tool
def search_talks(query: Annotated[str, "Search query — keywords, topic, or speaker name"]) -> str:
    """Search PyCon DE 2026 talks by keyword. Searches titles, abstracts, speaker names, and track names. Returns up to 10 matching talks."""
    results = _search_talks(query, _get_talks())
    if not results:
        return "No talks found matching that query."
    lines = []
    for r in results:
        lines.append(f"- **{r['title']}** by {r['speaker']} ({r['date']} {r['start']}, {r['room']})")
        if r.get("abstract"):
            lines.append(f"  Abstract: {r['abstract'][:150]}...")
    return "\n".join(lines)


@tool
def recommend_talks(profile: Annotated[str, "Description of the user's role, interests, or what they want to learn"]) -> str:
    """Get the full PyCon DE 2026 schedule with abstracts. Use this when the user asks for personalized recommendations — you'll receive all talks and should select the most relevant ones based on their profile."""
    results = _recommend_talks(profile, _get_talks())
    lines = [f"There are {len(results)} talks in total. Here are all of them:\n"]
    for r in results:
        entry = f"- **{r['title']}** by {r['speaker']} [{r['track'] or 'N/A'}] ({r['date']} {r['start']}, {r['room']})"
        if r.get("abstract"):
            entry += f"\n  {r['abstract']}"
        lines.append(entry)
    return "\n".join(lines)


@tool
def find_related(talk_title: Annotated[str, "Title (or partial title) of a talk the user enjoyed"]) -> str:
    """Find talks related to a specific PyCon DE 2026 talk. Returns talks with similar topics, same track, or overlapping themes."""
    results = _find_related(talk_title, _get_talks())
    if not results:
        return f"Could not find a talk matching '{talk_title}'. Try a different title or use search_talks first."
    lines = []
    for r in results:
        lines.append(f"- **{r['title']}** by {r['speaker']} [{r['track'] or 'N/A'}] ({r['date']} {r['start']}, {r['room']})")
        if r.get("abstract"):
            lines.append(f"  Abstract: {r['abstract'][:150]}...")
    return "\n".join(lines)


SYSTEM_PROMPT = """\
You are a helpful PyCon DE & PyData 2026 conference assistant. The conference took place \
April 14-16, 2026 in Darmstadt, Germany with ~120 talks across multiple tracks.

Your job is to help attendees discover talks they missed (most talks ran in parallel across \
5 rooms). You can search for talks, give personalized recommendations, and find talks related \
to ones they enjoyed.

When recommending talks, explain briefly WHY each talk is relevant to the user's interests. \
Be concise — 2-3 sentences per recommendation. Mention the speaker name and when/where it was."""


def create_agent():
    base_url = os.environ["OPENAI_BASE_URL"]
    http_client = httpx.Client(verify=False) if base_url.startswith("https://") else None
    llm = ChatOpenAI(
        base_url=base_url,
        api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
        model=os.environ.get("MODEL_NAME", "Salesforce/xLAM-2-32b-fc-r"),
        temperature=1.0,
        http_client=http_client,
    )
    tools = [search_talks, recommend_talks, find_related]
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


def main():
    console.print("[bold cyan]PyCon DE 2026 Talk Recommender[/bold cyan]")
    console.print(f"Loaded {len(_get_talks())} talks from schedule")
    console.print(f"Endpoint: {os.environ.get('OPENAI_BASE_URL', 'NOT SET')}")
    console.print("Type your question (or 'quit' to exit)\n")

    agent = create_agent()

    while True:
        try:
            question = console.input("[bold green]You:[/bold green] ")
        except (EOFError, KeyboardInterrupt):
            break

        if question.strip().lower() in ("quit", "exit", "q"):
            break

        console.print()
        response = agent.invoke({"messages": [("human", question)]})
        last_message = response["messages"][-1]
        console.print(Markdown(last_message.content))
        console.print()


if __name__ == "__main__":
    main()
