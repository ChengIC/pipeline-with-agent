"""Claude Agent 实现 - 集成 Claude Code Agent SDK"""
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass
from src.core.agent import AgentState, AgentResult, AgentContext
from src.agents.base import create_agent_task, AgentConfig


@dataclass
class ClaudeAgentConfig(AgentConfig):
    """Claude Agent 配置"""
    api_key: str = ""
    model: str = "claude-sonnet-4-20250514"
    max_iterations: int = 10
    tools: list = None  # 工具列表
    skills: list = None  # Skills 列表


class ClaudeAgent:
    """Claude Agent - 使用 @task 装饰器作为 Prefect Task"""

    def __init__(
        self,
        name: str,
        config: Optional[ClaudeAgentConfig] = None,
    ):
        self.name = name
        self.config = config or ClaudeAgentConfig(name=name)

    def create_task(self, execute_fn: Callable = None) -> Callable:
        """创建 Prefect Task

        Args:
            execute_fn: 自定义执行函数，如果未提供则使用默认逻辑

        Returns:
            Prefect Task 函数
        """
        def default_execute(sandbox, input_data: Any, context: AgentContext) -> AgentResult:
            """默认执行逻辑 - 可被覆盖"""
            from anthropic import Anthropic
            from src.core.agent import TOOL_REGISTRY, SKILL_REGISTRY

            client = Anthropic(api_key=self.config.api_key or None)

            # 构建消息
            messages = []
            if self.config.system_prompt:
                messages.append({
                    "role": "user",
                    "content": self.config.system_prompt
                })

            # 添加输入数据
            messages.append({
                "role": "user",
                "content": str(input_data)
            })

            # 调用 Claude API
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
            )

            return AgentResult(
                state=AgentState.COMPLETED,
                output=response.content[0].text if response.content else "",
            )

        # 使用提供的执行函数或默认
        actual_execute = execute_fn or default_execute

        # 创建 Prefect Task
        return create_agent_task(
            name=self.name,
            execute_fn=actual_execute,
            config=self.config
        )

    @property
    def task(self) -> Callable:
        """获取 Prefect Task"""
        return self.create_task()


def create_claude_agent_task(
    name: str,
    system_prompt: str = "",
    model: str = "claude-sonnet-4-20250514",
    execute_fn: Optional[Callable] = None,
) -> Callable:
    """快速创建 Claude Agent Task 的工厂函数

    Usage:
        generate_test_task = create_claude_agent_task(
            name="generate-test",
            system_prompt="Generate unit tests for the given code...",
            model="claude-sonnet-4-20250514",
        )

        @flow
        def my_pipeline():
            result = generate_test_task(
                sandbox_path=sandbox_path,
                input_data=code_input,
                previous_results={}
            )
    """
    config = ClaudeAgentConfig(
        name=name,
        system_prompt=system_prompt,
        model=model,
    )
    agent = ClaudeAgent(name=name, config=config)
    return agent.create_task(execute_fn)
