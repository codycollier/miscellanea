#!/usr/bin/env python
"""A prototype mini agent"""

import asyncio
import logging
import os
import random

from agents import Agent, RunConfig, Runner, function_tool, set_default_openai_key
from dotenv import load_dotenv


SYSTEM_PROMPT = """
You are a helpful assistant named Baz.
You can only discuss the get_color and get_number tools, or make polite conversation.
"""


@function_tool
def get_color() -> str:
    """Select and return a random color"""
    colors = ["red", "green", "blue", "yellow", "purple", "orange", "brown", "black", "white"]
    return random.choice(colors)


@function_tool
def get_number() -> int:
    """Select and return a random number integer"""
    return random.randint(0, 100)


async def agent_loop():
    """Main loop for the agent"""
    logging.basicConfig(level=logging.INFO)

    # Load the API key from the env file or environment variables
    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("BAZ_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("BAZ_OPENAI_API_KEY not found in environment variables")
    set_default_openai_key(api_key)

    # Initialize the agent core
    agent = Agent(
        name="ColorBot",
        instructions=SYSTEM_PROMPT,
        tools=[get_color, get_number],
        model="gpt-5-nano",
    )

    # Main interaction loop
    run_config = RunConfig(tracing_disabled=True)
    while True:
        user_input = input(">>> You: ")
        response = await Runner.run(agent, user_input, run_config=run_config)
        print(">>> Agent: ", response.final_output)


if __name__ == "__main__":
    asyncio.run(agent_loop())
