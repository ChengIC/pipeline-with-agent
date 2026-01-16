#!/usr/bin/env python3
"""
Unit Test Generation Agent Demo
================================

A harness demonstrating unit test generation with Claude Agent SDK.
Tests are generated in the same directory as the source file.

Example Usage:
    python demo.py --source ./my_module.py
    python demo.py --source ./my_module.py --model claude-sonnet-4-5-20250929
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_test_generation


# Configuration
DEFAULT_MODEL = "MiniMax-M2.1"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Unit Test Generation Agent - Generate pytest tests automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for a Python file (tests saved in same directory)
  python demo.py --source ./calculator.py

  # Use a specific model
  python demo.py --source ./calculator.py --model claude-sonnet-4-5-20250929

Environment Variables:
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
        """,
    )

    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source file to generate tests for",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nGet your API key from: https://console.anthropic.com/")
        print("\nThen set it:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    # Resolve source file path
    source_file = args.source.resolve()
    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        return

    print(f"Source file: {source_file}")

    # Run the test generation agent
    # project_dir is the same as source file's directory
    try:
        asyncio.run(
            run_test_generation(
                project_dir=source_file.parent,
                source_file=source_file,
                model=args.model,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
