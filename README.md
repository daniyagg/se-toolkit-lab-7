# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

### Optional

1. [Flutter Web Chatbot](./lab/tasks/optional/task-1.md)

## Deploy

The bot runs as a Docker container alongside the backend on your VM.

### Prerequisites

- VM with Docker and Docker Compose installed
- `.env.docker.secret` configured with all required variables
- `.env.bot.secret` with bot token and LLM credentials (for local testing)

### Environment variables

The bot service requires these variables in `.env.docker.secret`:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABCdef...` |
| `LMS_API_KEY` | Backend API key for authentication | `my-secret-key` |
| `LLM_API_KEY` | Qwen Code API key | `sk-...` |
| `LLM_API_BASE_URL` | LLM API endpoint | `http://host.docker.internal:42005/v1` |
| `LLM_API_MODEL` | Model name | `coder-model` |

> **Note:** `LLM_API_BASE_URL` must use `host.docker.internal` (not `localhost`) because the Qwen proxy runs on the host network, not inside the Docker network.

### Deploy commands

```terminal
# On your VM, navigate to the project directory
cd ~/se-toolkit-lab-7

# Stop any running bot process (from previous nohup deployment)
pkill -f "bot.py" 2>/dev/null || true

# Build and start all services (backend, postgres, caddy, bot)
docker compose --env-file .env.docker.secret up --build -d

# Check all services are running
docker compose --env-file .env.docker.secret ps

# Check bot logs for errors
docker compose --env-file .env.docker.secret logs bot --tail 50
```

### Verify deployment

```terminal
# Backend should still be healthy
curl -sf http://localhost:42002/docs

# Bot container should be running
docker ps | grep bot

# Test in Telegram: send /start, /health, or plain text like "what labs are available"
```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost`). |
| LLM queries fail | Use `host.docker.internal:42005` in `LLM_API_BASE_URL`. |
| Build fails at `uv sync` | Ensure `uv.lock` exists at project root. |
