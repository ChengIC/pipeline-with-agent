"""
Claude SDK Client Configuration
===============================

Functions for creating and configuring the Claude Agent SDK client
for unit test generation.
"""

import json
import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient


# Built-in tools for test generation
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(
    project_dir: Path,
    model: str,
    source_file: str = None,
) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client for unit test generation.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        source_file: Optional source file being tested (for system prompt)

    Returns:
        Configured ClaudeSDKClient
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Get your API key from: https://console.anthropic.com/"
        )

    # Create security settings
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                "Bash(*)",
            ],
        },
    }

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to file
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    # Custom system prompt based on source file
    system_prompt = "You are an expert at writing comprehensive Python unit tests using pytest."
    if source_file:
        system_prompt += f"\n\nYou are generating tests for: {source_file}"

    print(f"Created client for test generation")
    print(f"   - Project directory: {project_dir}")
    print(f"   - Model: {model}")
    print()

    return ClaudeSDKClient(
        options=ClaudeAgentOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=BUILTIN_TOOLS,
            max_turns=100,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
