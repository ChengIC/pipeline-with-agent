"""
Prompt Loading Utilities
========================

Functions for loading prompt templates for unit test generation.
"""

from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_test_generation_prompt(source_file: str, source_code: str) -> str:
    """
    Generate a prompt for unit test generation.

    Args:
        source_file: Path to the source file being tested
        source_code: The source code content

    Returns:
        Formatted prompt for test generation
    """
    template = load_prompt("test_generation")

    # Escape curly braces in source_code to prevent format() from parsing them
    escaped_code = source_code.replace("{", "{{").replace("}", "}}")

    # Use string replacement instead of format() to avoid brace parsing issues
    result = template.replace("{source_file}", source_file)
    result = result.replace("{source_code}", escaped_code)

    return result
