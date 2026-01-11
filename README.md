# Agent Pipeline System

A production-ready agent data processing pipeline built on **Prefect** framework. Features sandbox isolation, intelligent caching, multi-agent orchestration, and Streamlit monitoring dashboard.

## Features

- **Prefect Integration**: Leverage Prefect's built-in caching, retry, state management, and concurrency
- **Sandbox Isolation**: Filesystem and Docker sandbox environments
- **Claude Code Agent SDK**: Built-in integration with Claude agents
- **Tool/Skill Interface**: Extensible tool registry and skill templates
- **Conditional Pipeline**: Branch execution based on agent results
- **Streamlit Dashboard**: Real-time monitoring and analytics
- **Multi-MR Processing**: Configurable concurrency (sequential or parallel)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                 │
│         (Prefect Flow + Task Runner + Conditions)      │
├─────────────────────────────────────────────────────────┤
│                    Agent Layer                          │
│      (ClaudeAgent + Tool Registry + Skill Registry)    │
├─────────────────────────────────────────────────────────┤
│                   Sandbox Layer                         │
│           (FilesystemSandbox + DockerSandbox)          │
├─────────────────────────────────────────────────────────┤
│                 Prefect Infrastructure                  │
│    (Caching + Retry + State + Artifacts + Logging)     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pipeline-with-agent.git
cd pipeline-with-agent

# Install dependencies
pip install -e ".[dashboard]"  # Includes Streamlit for dashboard
```

### Basic Usage

```python
from src.examples import run_mr_test

# Run the MR test generation pipeline
results = run_mr_test(
    repo_url="https://github.com/example/repo.git",
    concurrency=1,  # 1=sequential, N=parallel MRs
)

# Check results
for name, result in results.items():
    print(f"{name}: {result.state.value}")
```

### Custom Pipeline

```python
from src.agents.claude_agent import create_claude_agent_task
from src.pipeline import create_pipeline, PipelineConfig

# Define agents
analyze_task = create_claude_agent_task(
    name="analyze",
    system_prompt="Analyze the code and provide a summary.",
)

test_task = create_claude_agent_task(
    name="test",
    system_prompt="Generate unit tests for the code.",
)

# Create pipeline
pipeline = create_pipeline(
    PipelineConfig(
        name="custom-pipeline",
        agents=[analyze_task, test_task],
        concurrency=1,
        cache_enabled=True,
    )
)

# Execute
results = pipeline(sandbox_input="https://github.com/example/repo.git")
```

## Project Structure

```
pipeline-with-agent/
├── src/
│   ├── core/              # Core abstractions
│   │   ├── agent.py       # Agent data classes + registry
│   │   ├── sandbox.py     # Sandbox abstract + config
│   │   └── cache.py       # Cache key functions
│   ├── agents/
│   │   ├── base.py        # Agent Task base class
│   │   └── claude_agent.py # Claude Agent implementation
│   ├── sandbox/
│   │   └── filesystem.py  # FilesystemSandbox
│   ├── pipeline/
│   │   ├── flow.py        # Pipeline factory
│   │   └── conditions.py  # Conditional branching
│   └── examples/
│       └── mr_test_generator.py # Complete example
├── dashboard/
│   └── app.py             # Streamlit Dashboard
├── docs/
│   └── claude.md          # Claude SDK integration guide
├── config.yaml            # Configuration file
├── requirements.txt
└── pyproject.toml
```

## Configuration

Edit `config.yaml` to customize:

```yaml
pipeline:
  max_retries: 3
  retry_delay_seconds: 5
  concurrency: 1  # 1=sequential, N=parallel
  timeout_seconds: 3600

sandbox:
  type: filesystem
  base_dir: ./sandbox
  auto_cleanup: true

agent:
  default_model: claude-sonnet-4-20250514
  temperature: 0.7
  max_iterations: 10

dashboard:
  host: 0.0.0.0
  port: 8501
```

## Running the Dashboard

```bash
# Start the Streamlit dashboard
streamlit run dashboard/app.py

# Dashboard provides:
# - Real-time flow run monitoring
# - Task details and artifacts
# - Analytics and metrics
# - Pipeline configuration UI
```

## Prefect Features Used

| Feature | Usage |
|---------|-------|
| `@task` decorator | Wrap agents as Prefect tasks |
| `cache_key_fn` | Automatic result caching |
| `retry_delay_seconds` | Automatic retry on failure |
| `timeout_seconds` | Task timeout handling |
| `TaskRunner` | Sequential/Concurrent execution |
| `State Machine` | Track pipeline state |
| `Artifacts` | Store agent outputs |

## Example: MR Test Generator

The `mr_test_generator.py` example demonstrates:

1. **Clone Agent**: Clone repository to sandbox
2. **Generate Agent**: Create unit tests
3. **Validate Agent**: Check for fail-to-pass cases
4. **Iterate Agent**: Improve tests based on feedback

```python
from src.examples import create_mr_test_pipeline

# Create pipeline with conditional execution
pipeline = create_mr_test_pipeline(
    concurrency=1,
    cache_enabled=True,
)

# Run
results = pipeline(sandbox_input="https://github.com/example/repo.git")
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `PREFECT_API_URL` | Prefect API URL |
| `PREFECT_HOME` | Prefect configuration directory |

## Documentation

- [Claude SDK Integration](docs/claude.md) - Tool and skill registration
- [API Reference](docs/api.md) - Coming soon
- [Examples](src/examples/) - Usage examples

## License

MIT
