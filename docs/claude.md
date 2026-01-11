# Claude Code Agent SDK Integration

This document describes how to integrate Claude Code Agent SDK with the Agent Pipeline system, including tool registration, skills interface, and customization options.

## Overview

The pipeline uses **Claude Code Agent SDK** as the default intelligent agent. Each agent is wrapped as a Prefect Task, enabling:
- Automatic caching and retry
- Distributed execution
- State tracking
- Integration with Prefect Cloud

## Quick Start

### Basic Claude Agent

```python
from src.agents.claude_agent import create_claude_agent_task

# Create a simple agent task
analyze_task = create_claude_agent_task(
    name="analyze-code",
    system_prompt="Analyze the code and provide a summary of functionality.",
    model="claude-sonnet-4-20250514",
)

# Use in pipeline
from src.pipeline import create_pipeline, PipelineConfig

pipeline = create_pipeline(
    PipelineConfig(
        name="analysis-pipeline",
        agents=[analyze_task],
    )
)

result = pipeline(sandbox_input="https://github.com/example/repo.git")
```

## Tool Registry

Tools are functions that agents can call to interact with the sandbox environment.

### Registering a Tool

```python
from src.core.agent import register_tool

def read_file_content(sandbox, input_data, context):
    """Read a file from the sandbox and return its content."""
    file_path = input_data.get("file_path")
    if not file_path:
        raise ValueError("file_path is required")

    content = sandbox.read_file(file_path)
    return {"content": content, "path": file_path}

# Register the tool
register_tool("read_file", read_file_content)
```

### Using Tools in Agent Prompt

```python
test_agent = create_claude_agent_task(
    name="generate-tests",
    system_prompt="""You have access to a 'read_file' tool that lets you read files
from the sandbox. Use it to understand the code structure before generating tests.

For example:
- First read the main module files
- Understand the function signatures
- Generate appropriate test cases

Remember to write tests to the sandbox using the write_file tool.""",
)
```

### Built-in Tools Available

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `read_file` | Read file content from sandbox | `{"file_path": "path/to/file.py"}` |
| `write_file` | Write content to sandbox | `{"path": "path/to/file.py", "content": "..."}` |
| `list_files` | List files in directory | `{"pattern": "**/*.py"}` |
| `execute_command` | Run shell command | `{"command": "python -m pytest"}` |

## Skills Interface

Skills are prompt templates that provide specialized capabilities to agents.

### Registering a Skill

```python
from src.core.agent import register_skill

# Register a code analysis skill
register_skill(
    name="analyze_code",
    prompt="""You are a code analysis expert. Analyze the following code and provide:
1. Summary of functionality (2-3 sentences)
2. List of key functions/classes
3. Potential edge cases
4. Suggestions for improvement

Code to analyze:
{code}

Provide your analysis in JSON format:
{
    "summary": "...",
    "functions": [...],
    "edge_cases": [...],
    "suggestions": [...]
}"""
)
```

### Using Skills in Agent

```python
from src.agents.claude_agent import ClaudeAgent

agent = ClaudeAgent(
    name="code-analyzer",
    config={
        "system_prompt": "Use the analyze_code skill to analyze the provided code.",
    }
)

# Skills are automatically included when the agent processes input
```

### Skill Parameters

Skills can use parameters that are filled at runtime:

```python
register_skill(
    name="generate_tests_for_file",
    prompt="""Generate pytest tests for the following file:

File path: {file_path}
Language: {language}

Generate comprehensive tests including:
- Unit tests for each function
- Edge case tests
- Mock any external dependencies""",
)
```

## Custom Agent Execution

For more control, you can define custom execution functions:

```python
from src.core.agent import AgentState, AgentResult

def custom_test_execution(sandbox, input_data, context):
    """Custom agent logic with full control."""

    # 1. Read input files
    code = sandbox.read_file("src/main.py")

    # 2. Process with custom logic
    tests = generate_tests(code)  # Your logic here

    # 3. Write output
    sandbox.write_file("tests/test_main.py", tests)

    # 4. Run tests
    returncode, stdout, stderr = sandbox.execute("pytest tests/")

    # 5. Return result
    passed = "passed" in stdout
    return AgentResult(
        state=AgentState.COMPLETED if passed else AgentState.FAILED,
        output=tests,
        metrics={"passed": int(passed), "failed": int(not passed)},
    )

# Create agent task with custom execution
from src.agents.base import create_agent_task

custom_agent = create_agent_task(
    name="custom-test-gen",
    execute_fn=custom_test_execution,
)
```

## Configuration Options

### ClaudeAgentConfig

```python
from src.agents.claude_agent import ClaudeAgentConfig

config = ClaudeAgentConfig(
    name="my-agent",
    system_prompt="You are a helpful assistant.",
    api_key="",  # Uses ANTHROPIC_API_KEY env var if empty
    model="claude-sonnet-4-20250514",
    temperature=0.7,
    max_tokens=4096,
    max_iterations=10,
    tools=[],  # List of tool names
    skills=[],  # List of skill names
)
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `PREFECT_API_URL` | Prefect API URL (default: http://127.0.0.1:4200) |
| `PREFECT_HOME` | Prefect configuration directory |

## Examples

### Complete MR Test Generator

See `src/examples/mr_test_generator.py` for a complete example:

```python
from src.examples import run_mr_test

# Run the MR test generation pipeline
results = run_mr_test(
    repo_url="https://github.com/anthropics/claude-code.git",
    concurrency=1,  # 1=sequential, N=parallel MRs
)

# Check results
for name, result in results.items():
    print(f"{name}: {result.state.value}")
```

### Multi-Agent Pipeline

```python
from src.agents.claude_agent import create_claude_agent_task
from src.pipeline import create_pipeline, PipelineConfig

# Define agents
clone_task = create_claude_agent_task(
    name="clone",
    system_prompt="Clone the repository to sandbox.",
)

analyze_task = create_claude_agent_task(
    name="analyze",
    system_prompt="Analyze the codebase structure.",
)

test_task = create_claude_agent_task(
    name="test",
    system_prompt="Generate unit tests.",
)

# Create pipeline
pipeline = create_pipeline(
    PipelineConfig(
        name="multi-agent-pipeline",
        agents=[clone_task, analyze_task, test_task],
        concurrency=1,
    )
)

# Execute
results = pipeline(sandbox_input="https://github.com/example/repo.git")
```

## Best Practices

1. **Tool Design**: Keep tools focused on single tasks
2. **Skill Templates**: Make skills generic with parameter substitution
3. **Error Handling**: Return `AgentResult` with proper error messages
4. **Metrics**: Include metrics for monitoring and debugging
5. **Cache Keys**: Let Prefect handle caching automatically

## Troubleshooting

### API Key Issues

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"
```

### Sandbox Not Initialized

Ensure the pipeline initializes the sandbox before agent execution:

```python
# The pipeline automatically handles sandbox setup/teardown
# No manual intervention required
```

### Tool Not Found

Register tools before creating agent tasks:

```python
from src.core.agent import register_tool

# Register early in your application
register_tool("my_tool", my_tool_function)
```
