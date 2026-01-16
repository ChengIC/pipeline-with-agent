"""
Agent Session Logic
===================

Core agent interaction functions for running unit test generation sessions.
"""

import asyncio
from pathlib import Path
from typing import Optional, Tuple

from claude_agent_sdk import ClaudeSDKClient

from client import create_client
from prompts import get_test_generation_prompt

from dotenv import load_dotenv
load_dotenv()

async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
) -> Tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text) where status is:
        - "success" if tests were generated successfully
        - "error" if an error occurred
    """
    print("Sending prompt to Claude Agent SDK...\n")

    try:
        await client.query(message)

        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__

            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "success", response_text

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e)


async def run_test_generation(
    project_dir: Path,
    source_file: Path,
    model: str,
) -> None:
    """
    Run unit test generation for a source file.

    Args:
        project_dir: Directory for the project
        source_file: Path to the source file to generate tests for
        model: Claude model to use
    """
    print("\n" + "=" * 70)
    print("  UNIT TEST GENERATION AGENT")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Source file: {source_file}")
    print(f"Model: {model}")
    print()

    # Read source file
    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        return

    source_code = source_file.read_text()
    source_file_name = source_file.name

    # Create client
    client = create_client(project_dir, model, source_file_name)

    # Get prompt
    prompt = get_test_generation_prompt(str(source_file), source_code)

    # Run session
    async with client:
        status, response = await run_agent_session(client, prompt)

    # Handle status
    if status == "success":
        print("\n" + "=" * 70)
        print("  TEST GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nSource file: {source_file}")
        print(f"Project directory: {project_dir}")
        print("\nCheck the project directory for generated test files.")
    else:
        print("\nTest generation encountered an error.")

    print("\nDone!")
