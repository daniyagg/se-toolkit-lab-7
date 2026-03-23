# Development Plan: LMS Telegram Bot

## Overview

This document outlines the implementation plan for building a Telegram bot that interfaces with the LMS (Learning Management System) backend. The bot enables students to check system health, browse labs and scores, and ask questions in plain language using an LLM for intent routing.

## Task 1: Scaffold and Test Mode

**Goal:** Establish a testable handler architecture with CLI test mode.

**Approach:**
- Create handler functions that are pure — they take input (command string) and return output (text response) without depending on Telegram
- Build `bot.py` as the entry point with `--test` flag support for offline verification
- Separate concerns: handlers don't import Telegram libraries, making them testable and reusable
- Implement placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`

**Why this matters:** Testable handlers mean we can verify logic without a Telegram connection. The same handler function works in `--test` mode, unit tests, and the real Telegram bot.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
- Create an API client in `bot/services/lms_client.py` that makes HTTP requests to the backend
- Use Bearer token authentication with `LMS_API_KEY` from environment
- Update `/health` to call `GET /health` endpoint and report real status
- Implement `/labs` to fetch available labs from `GET /items`
- Implement `/scores <lab>` to fetch per-task pass rates
- Add error handling: backend down produces friendly messages, not crashes

**Architecture:** The handler layer calls the service layer (API client). Handlers remain transport-agnostic — they don't know about Telegram or HTTP, they just call functions and return text.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Enable plain text queries using LLM tool use.

**Approach:**
- Create an LLM client in `bot/services/llm_client.py`
- Define tool descriptions for each backend endpoint (e.g., "get_labs: list available labs")
- Build an intent router that sends user text to the LLM with tool descriptions
- The LLM decides which tool to call based on the description quality
- Parse LLM response and execute the appropriate handler

**Key insight:** The LLM reads tool descriptions to decide which action to take. Description quality matters more than prompt engineering. Don't use regex or keyword matching — let the LLM do the routing based on well-written tool descriptions.

## Task 4: Containerize and Deploy

**Goal:** Deploy the bot on the VM using Docker Compose.

**Approach:**
- Create `bot/Dockerfile` using Python base image
- Add bot as a service in `docker-compose.yml`
- Configure container networking: bot uses service name `backend` not `localhost`
- Mount `.env.bot.secret` for secrets (gitignored)
- Document deployment process in README

**Docker networking:** Containers communicate via service names defined in `docker-compose.yml`. The bot container reaches the backend at `http://backend:42002`, not `localhost:42002`.

## Testing Strategy

1. **Unit tests:** Test handlers in isolation with mocked services
2. **Test mode:** `uv run bot.py --test "/command"` for quick verification
3. **Integration tests:** Deploy to VM and test in real Telegram

## File Structure

```
bot/
├── bot.py              # Entry point: Telegram startup + --test mode
├── config.py           # Environment variable loading
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start handler
│   ├── help.py         # /help handler
│   ├── health.py       # /health handler
│   ├── labs.py         # /labs handler
│   └── scores.py       # /scores handler
├── services/
│   ├── __init__.py
│   ├── lms_client.py   # Backend API client
│   └── llm_client.py   # LLM API client (Task 3)
└── tests/              # Unit tests (optional)
```
