# PyCon DE 2026 Talk Recommender

SLM-powered conference assistant using [xLAM 2 32B](https://huggingface.co/Salesforce/xLAM-2-32b-fc-r) with tool calling, deployed on European sovereign cloud infrastructure ([Leaf Cloud](https://leaf.cloud), Amsterdam).

Built as a live demo for an Ilionx lunch colloquium on Small Language Models, agent architecture, and sovereign cloud — based on learnings from PyCon DE & PyData 2026.

## Architecture

```
User → LangChain ReAct Agent → OpenAI-compatible API (vLLM on Leaf Cloud GPU)
                ↓
        3 tools: search_talks, recommend_talks, find_related
                ↓
        PyCon DE 2026 schedule (132 talks, 3 days, 20 tracks)
```

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run tests (no GPU needed)
uv run pytest -v

# Run the interactive agent (requires endpoint)
cp .env.example .env
# Edit .env with your endpoint
source .env && uv run python -m pycon_agent.agent
```

## Infrastructure

The `infra/` directory contains Terraform configuration for provisioning a GPU VM on Leaf Cloud with vLLM:

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit with your Leaf Cloud credentials
terraform init && terraform apply
```

## Fallback

If the Leaf Cloud endpoint is unavailable, swap to Azure AI Foundry by changing the env vars — the agent uses the OpenAI SDK so any compatible endpoint works.

## License

MIT
