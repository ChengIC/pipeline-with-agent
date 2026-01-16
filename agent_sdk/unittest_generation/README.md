# Unit Test Generation Agent

A lightweight harness for generating unit tests using Claude Agent SDK.

## Structure

```
unittest_generation/
├── __init__.py          # Package initialization
├── agent.py             # Agent session logic
├── client.py            # SDK client configuration
├── demo.py              # Entry point script
├── prompts.py           # Prompt loading utilities
├── prompts/
│   └── test_generation.md  # Test generation prompt template
└── requirements.txt     # Dependencies
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

3. Run the test generator:
```bash
python demo.py --source ./your_module.py
```

## Usage

```bash
# Generate tests for a Python file
python demo.py --source ./calculator.py

# Save tests to specific directory
python demo.py --source ./calculator.py --output ./tests

# Use a specific model
python demo.py --source ./calculator.py --model claude-sonnet-4-5-20250929
```

## Programmatic Usage

```python
import asyncio
from pathlib import Path
from agent_sdk.unittest_generation import run_test_generation

async def main():
    await run_test_generation(
        project_dir=Path("./tests"),
        source_file=Path("./my_module.py"),
        model="claude-sonnet-4-5-20250929"
    )

asyncio.run(main())
```

## Demo

An example Python module is provided in `data/example_repo/calculator.py` for testing:

```bash
# Run from the unittest_generation directory
cd agent_sdk/unittest_generation

# Generate tests for the example calculator
python demo.py --source ../../data/example_repo/calculator.py

# Run the generated tests
cd ../../data/example_repo
pytest -v
```

Generated test file will be saved as `data/example_repo/test_calculator.py`.

## Features

- Generates comprehensive pytest unit tests
- Covers public functions and classes
- Tests edge cases and error conditions
- Uses pytest fixtures and parametrize
- Includes mock patterns for external dependencies
