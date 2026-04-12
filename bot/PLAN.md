# LMS Telegram Bot — Development Plan

## Overview

This document describes the approach for building a Telegram bot that interfaces with the LMS backend. The bot provides slash commands (`/health`, `/labs`, `/scores`) and natural language query support via an LLM. Each task builds on the previous one.

## Task 1: Plan and Scaffold (Current)

**Goal:** Create the project skeleton with testable handlers.

**Approach:** Handlers are plain functions that take input and return text. They have no dependency on Telegram, which means they can be tested via `--test` mode, unit tests, or the Telegram bot — same functions, different entry points. This is the *separation of concerns* pattern.

**Deliverables:** `bot.py` with `--test` mode, `handlers/` directory, `services/` directory, `config.py`, `pyproject.toml`, and this plan.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:** Create an API client in `bot/services/api_client.py` that makes HTTP requests to the LMS backend. The client reads `LMS_API_BASE_URL` and `LMS_API_KEY` from environment variables and uses Bearer token authentication. Handlers will call the API client instead of returning placeholder text. Error handling is critical — if the backend is unreachable, the bot should return a clear error message rather than crashing.

**Deliverables:** API client service, updated `/health` handler (real backend check), updated `/labs` handler (real lab list), updated `/scores` handler (real scores lookup).

## Task 3: Intent Routing with LLM

**Goal:** The bot understands plain text questions, not just slash commands.

**Approach:** Use an LLM with tool calling. The system prompt describes available tools (e.g., "get_lab_scores", "list_labs", "get_health") and the LLM decides which tool to call based on the user's message. Tool descriptions are the key — they need to be clear enough that the LLM picks the right one. This is the *tool use* pattern: the LLM acts as an intent router.

**Deliverables:** LLM client service, intent router handler, tool definitions, updated `--test` mode that works with natural language queries like "what labs are available".

## Task 4: Deployment

**Goal:** Run the bot in Docker alongside the backend.

**Approach:** Add a `bot` service to `docker-compose.yml`. The bot container communicates with the backend using Docker service names (not `localhost` — containers have their own network namespace). Environment variables are injected via `.env.bot.secret`. The bot runs in Telegram mode (not `--test` mode) and stays running as a long-lived process.

**Deliverables:** Docker configuration, updated `bot.py` with Telegram mode implementation, deployment documentation.

## Architecture Summary

```
Telegram → bot.py (Telegram mode) → process_command() → handlers/ → services/
CLI      → bot.py (--test mode)   → process_command() → handlers/ → services/
```

The `process_command()` function is the shared routing layer. Handlers are pure functions. Services handle external communication (LMS API, LLM API). This layered architecture keeps each piece testable in isolation.
