#!/usr/bin/env python
"""A prototype mini agent using the Anthropic API


Note: This is a single-shot port (using Opus 4.5) of the colorbot.py agent.
"""

import json
import logging
import os
import random

import anthropic
from dotenv import load_dotenv


SYSTEM_PROMPT = """
You are a helpful assistant named Baz.
You can only discuss the get_color and get_number tools, or make polite conversation.
"""

# Define tools for Anthropic's tool use format
TOOLS = [
    {
        "name": "get_color",
        "description": "Select and return a random color",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_number",
        "description": "Select and return a random integer between 0 and 100",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def get_color() -> str:
    """Select and return a random color"""
    colors = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "black", "white"]
    return random.choice(colors)


def get_number() -> int:
    """Select and return a random number integer"""
    return random.randint(0, 100)


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name and return the result as a string"""
    if tool_name == "get_color":
        return get_color()
    elif tool_name == "get_number":
        return str(get_number())
    else:
        return f"Unknown tool: {tool_name}"


def agent_loop():
    """Main loop for the agent"""
    logging.basicConfig(level=logging.INFO)

    # Load the API key from the env file or environment variables
    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("BAZ_ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("BAZ_ANTHROPIC_API_KEY not found in environment variables")

    # Initialize the Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Main interaction loop
    while True:
        user_input = input(">>> You: ")

        # Build the initial messages
        messages = [{"role": "user", "content": user_input}]

        # Call the API and handle tool use in a loop
        while True:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            # Check if we need to handle tool use
            if response.stop_reason == "tool_use":
                # Process all tool use blocks in the response
                tool_results = []
                assistant_content = response.content

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        # Execute the tool
                        result = execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result,
                        })

                # Add assistant message and tool results to conversation
                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # No more tool calls, extract the final text response
                final_output = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_output += block.text

                print(">>> Agent: ", final_output)
                break


if __name__ == "__main__":
    agent_loop()

