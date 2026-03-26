"""LLM API client for intent routing.

Task 3: Implement LLM client for natural language understanding.
"""

import json
import sys

import httpx

from config import settings


# Tool definitions for all 9 backend endpoints
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get a list of all available labs and tasks. Use this when the user asks about what labs exist, what's available, or needs to browse the catalog.",
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
            "description": "Get a list of all enrolled learners and their groups. Use this when the user asks about students, enrollment, or how many people are in the course.",
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
            "description": "Get score distribution (4 buckets) for a specific lab. Use this when the user asks about score distribution, how scores are spread, or histogram data for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average pass rates and attempt counts for a specific lab. Use this when the user asks about pass rates, success rates, difficulty, or how students are performing on a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab. Use this when the user asks about when students submitted, activity over time, or submission patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab. Use this when the user asks about group performance, which group is better, or compare groups.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab. Use this when the user asks about top students, leaderboard, best performers, or who is doing the best.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of learners to return, default 10",
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
            "description": "Get completion rate percentage for a specific lab. Use this when the user asks about completion rate, how many finished, or what percentage completed a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from the autochecker. Use this when the user asks to sync, update, or refresh the data, or if data seems stale.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM to understand its role and how to use tools
SYSTEM_PROMPT = """You are an intelligent assistant for a Learning Management System (LMS). Your job is to help users get information about labs, scores, learners, and analytics.

You have access to tools that fetch data from the LMS backend. When a user asks a question:
1. Think about what information you need to answer
2. Call the appropriate tool(s) to get that information
3. Once you have the tool results, use them to formulate a clear, helpful answer

Important rules:
- Always call tools to get real data before answering questions about labs, scores, or learners
- If you need data from multiple labs (e.g., comparing labs), call tools for each one
- If the user's question is unclear or ambiguous, ask for clarification
- If the user greets you or asks a simple question, respond naturally without using tools
- Present data in a clear, readable format with key numbers highlighted

Available tools are listed below. Use them to answer user questions."""


class LLMClient:
    """Client for the LLM API."""

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url.rstrip("/")
        self.model = settings.llm_api_model

    def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> dict:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions.

        Returns:
            Dict with 'content' (str) and/or 'tool_calls' (list).
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        message = choice["message"]

        result = {"content": message.get("content", "")}

        if "tool_calls" in message and message["tool_calls"]:
            result["tool_calls"] = message["tool_calls"]

        return result

    def route_intent(
        self, user_message: str, debug: bool = False
    ) -> str:
        """Route user intent using LLM with tool calling.

        This implements the tool calling loop:
        1. Send user message + tool definitions to LLM
        2. LLM decides which tool(s) to call
        3. Execute the tool(s)
        4. Feed results back to LLM
        5. LLM produces final answer

        Args:
            user_message: The user's natural language input.
            debug: If True, print debug info to stderr.

        Returns:
            The final response text.
        """

        def log(msg: str) -> None:
            if debug:
                print(msg, file=sys.stderr)

        # Initialize conversation with system prompt
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM with conversation history and tools
            log(f"[iteration {iteration}] Calling LLM...")
            result = self.chat(conversation, tools=TOOL_DEFINITIONS)

            # Check if LLM wants to call tools
            tool_calls = result.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - LLM has a final answer
                log(f"[summary] LLM returned final answer")
                return result["content"]

            # Add assistant's message with tool calls to conversation
            conversation.append(
                {
                    "role": "assistant",
                    "content": result["content"],
                    "tool_calls": tool_calls,
                }
            )

            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = json.loads(function.get("arguments", "{}"))

                log(f"[tool] LLM called: {tool_name}({tool_args})")

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_args)

                log(f"[tool] Result: {str(tool_result)[:200]}...")

                # Add tool result to conversation
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_result),
                    }
                )

            log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        # If we reach here, we hit max iterations
        return "I'm having trouble processing your request. Please try rephrasing your question."

    def _execute_tool(self, name: str, args: dict) -> dict:
        """Execute a tool by name with the given arguments.

        Args:
            name: The tool name (e.g., "get_items").
            args: Tool arguments as a dict.

        Returns:
            The tool result as a dict.
        """
        from services.lms_client import LMSClient

        client = LMSClient()

        tool_methods = {
            "get_items": lambda: client.get_items(),
            "get_learners": lambda: client.get_learners(),
            "get_scores": lambda: client.get_scores(args.get("lab", "")),
            "get_pass_rates": lambda: client.get_pass_rates(args.get("lab", "")),
            "get_timeline": lambda: client.get_timeline(args.get("lab", "")),
            "get_groups": lambda: client.get_groups(args.get("lab", "")),
            "get_top_learners": lambda: client.get_top_learners(
                args.get("lab", ""), args.get("limit", 10)
            ),
            "get_completion_rate": lambda: client.get_completion_rate(
                args.get("lab", "")
            ),
            "trigger_sync": lambda: client.trigger_sync(),
        }

        if name not in tool_methods:
            return {"error": f"Unknown tool: {name}"}

        try:
            result = tool_methods[name]()
            return result
        except Exception as e:
            return {"error": str(e)}
