"""Run the 3 demo queries against the live endpoint and print results.

Usage: source .env && uv run python scripts/test_live.py
"""

import os
import time

from rich.console import Console
from rich.markdown import Markdown

from pycon_agent.agent import create_agent

console = Console()

DEMO_QUERIES = [
    ("search_talks", "Which talks at PyCon were about observability?"),
    ("recommend_talks", "I'm a data engineer working on compliance in healthcare. Which talks should I watch back?"),
    ("find_related", "I really liked the sovereignty keynote by Aaron Glenn. What else should I watch?"),
]


def main():
    console.print("[bold cyan]Live Demo Test[/bold cyan]")
    console.print(f"Endpoint: {os.environ.get('OPENAI_BASE_URL', 'NOT SET')}")
    console.print(f"Model: {os.environ.get('MODEL_NAME', 'NOT SET')}\n")

    agent = create_agent()

    for expected_tool, query in DEMO_QUERIES:
        console.rule(f"[bold]{expected_tool}[/bold]")
        console.print(f"[green]Query:[/green] {query}\n")

        start = time.time()
        response = agent.invoke({"messages": [("human", query)]})
        elapsed = time.time() - start

        last_message = response["messages"][-1]
        console.print(Markdown(last_message.content))
        console.print(f"\n[dim]Time: {elapsed:.1f}s[/dim]\n")

        tool_calls = [
            m for m in response["messages"]
            if hasattr(m, "tool_calls") and m.tool_calls
        ]
        if tool_calls:
            tools_used = [tc["name"] for m in tool_calls for tc in m.tool_calls]
            console.print(f"[dim]Tools used: {', '.join(tools_used)}[/dim]\n")


if __name__ == "__main__":
    main()
