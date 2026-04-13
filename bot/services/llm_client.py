"""LLM client service with tool calling support.

Sends user messages to the LLM with tool definitions, executes tool calls,
feeds results back, and returns the final answer.
"""

import json
import sys
from typing import Any

import httpx

from config import get_llm_api_base_url, get_llm_api_key, get_llm_api_model
from services.api_client import APIClient


# ── Tool schemas ──────────────────────────────────────────────────────────────
# Each schema describes one backend endpoint as a function the LLM can call.
# The LLM reads these descriptions to decide which tool to use.

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List all labs and tasks available in the system. Returns items with their IDs and names. Use this when the user asks what labs exist, what tasks are available, or needs an overview.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "List enrolled students and their groups. Use when the user asks about students, learners, enrollments, or groups without specifying a lab.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab. Returns how many students scored in each range. Use when the user asks about scores, grade distribution, or how students performed in a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Always use the exact lab ID format.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab. Shows which tasks students pass or fail most often. Use when the user asks about pass rates, task difficulty, average scores per task, or which tasks are hardest in a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a specific lab. Shows activity over time. Use when the user asks about submission timeline, activity over time, when students submitted, or daily submission counts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab. Shows which group is performing better. Use when the user asks about groups, group comparison, which group is best, or group performance in a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab. Returns a leaderboard. Use when the user asks about top students, best performers, leaderboard, or who is doing best in a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return. Default 10 if not specified.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab. Shows what fraction of students finished the lab. Use when the user asks about completion rate, how many students finished, or completion percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger a data sync from the autochecker to refresh all data. Use when the user asks to sync, refresh, update data, or pull latest results from the autochecker.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an LMS assistant. "
    "Use tools to get real data from the backend API. "
    "When asked a question, call the right tool(s), then summarize the results with specific numbers. "
    "For greetings, respond warmly. For unclear input, explain what you can do. "
    "Always use tools — don't make up answers. "
    "Keep responses concise."
)


class LLMClient:
    """Client for LLM-based intent routing.

    Takes a user message, sends it to the LLM with tool definitions,
    executes tool calls, feeds results back, and returns the final answer.
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.base_url = get_llm_api_base_url().rstrip("/")
        self.api_key = get_llm_api_key()
        self.model = get_llm_api_model()

        # Map tool names to methods that execute them
        self._tool_handlers = {
            "get_items": self._handle_get_items,
            "get_learners": self._handle_get_learners,
            "get_scores": self._handle_get_scores,
            "get_pass_rates": self._handle_get_pass_rates,
            "get_timeline": self._handle_get_timeline,
            "get_groups": self._handle_get_groups,
            "get_top_learners": self._handle_get_top_learners,
            "get_completion_rate": self._handle_get_completion_rate,
            "trigger_sync": self._handle_trigger_sync,
        }

    def _debug(self, msg: str) -> None:
        """Print debug message to stderr (visible in --test mode)."""
        print(msg, file=sys.stderr)

    def _headers(self) -> dict:
        """Return headers for LLM API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ── Tool execution handlers ───────────────────────────────────────────

    async def _handle_get_items(self, args: dict) -> Any:
        data, err = self.api_client.get_items()
        if err:
            return {"error": err}
        return data

    async def _handle_get_learners(self, args: dict) -> Any:
        data, err = self.api_client.get_learners()
        if err:
            return {"error": err}
        return data

    async def _handle_get_scores(self, args: dict) -> Any:
        data, err = self.api_client.get_scores(args.get("lab"))
        if err:
            return {"error": err}
        return data

    async def _handle_get_pass_rates(self, args: dict) -> Any:
        data, err = self.api_client.get_pass_rates(args.get("lab"))
        if err:
            return {"error": err}
        return data

    async def _handle_get_timeline(self, args: dict) -> Any:
        data, err = self.api_client.get_timeline(args.get("lab"))
        if err:
            return {"error": err}
        return data

    async def _handle_get_groups(self, args: dict) -> Any:
        data, err = self.api_client.get_groups(args.get("lab"))
        if err:
            return {"error": err}
        return data

    async def _handle_get_top_learners(self, args: dict) -> Any:
        data, err = self.api_client.get_top_learners(
            args.get("lab"), args.get("limit", 10)
        )
        if err:
            return {"error": err}
        return data

    async def _handle_get_completion_rate(self, args: dict) -> Any:
        data, err = self.api_client.get_completion_rate(args.get("lab"))
        if err:
            return {"error": err}
        return data

    async def _handle_trigger_sync(self, args: dict) -> Any:
        data, err = self.api_client.trigger_sync()
        if err:
            return {"error": err}
        return data

    # ── Core tool-calling loop ────────────────────────────────────────────

    async def route(self, user_message: str) -> str:
        """Route a user message through the LLM tool-calling loop.

        1. Send message + tool definitions to LLM
        2. If LLM calls tools → execute them, feed results back, repeat
        3. If LLM returns text → that's the final answer
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 10  # Prevent infinite loops

        for iteration in range(max_iterations):
            # Call the LLM
            response = await self._call_llm(messages)

            if response is None:
                return "⚠️ LLM service error. Please try again later."

            # Check if the LLM wants to call tools
            choice = response["choices"][0]
            message = choice["message"]
            tool_calls = message.get("tool_calls")

            if not tool_calls:
                # No tool calls — this is the final answer
                content = message.get("content", "")
                if content:
                    return content
                return "I'm not sure how to help with that. Try asking about labs, scores, students, or groups."

            # Execute each tool the LLM requested
            messages.append(message)  # Add the assistant's message with tool_calls

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                tool_id = tool_call["id"]

                self._debug(f"[tool] LLM called: {tool_name}({json.dumps(tool_args)})")

                # Execute the tool
                handler = self._tool_handlers.get(tool_name)
                if handler:
                    result = await handler(tool_args)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                self._debug(f"[tool] Result: {json.dumps(result)[:200]}")

                # Feed result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": json.dumps(result),
                })

            self._debug(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        return "⚠️ I couldn't complete that request — too many steps. Try a simpler question."

    async def _call_llm(self, messages: list[dict]) -> dict | None:
        """Make a single call to the LLM API.

        Returns the parsed JSON response, or None on error.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOL_SCHEMAS,
            "max_tokens": 500,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            self._debug(f"[llm] connection refused ({self.base_url})")
            return None
        except httpx.HTTPStatusError as e:
            self._debug(f"[llm] HTTP {e.response.status_code}: {e.response.text[:500]}")
            return None
        except Exception as e:
            self._debug(f"[llm] error: {type(e).__name__}: {e}")
            return None
