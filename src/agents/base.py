"""智能体基类 - 使用 Prefect @task 装饰器"""
from prefect import task
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass
from src.core.agent import AgentState, AgentResult


@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    model: str = "claude-sonnet-4-20250514"


def create_agent_task(
    name: str,
    execute_fn: Callable,
    config: AgentConfig = None
):
    """创建 Agent Task 的工厂函数

    利用 Prefect 的:
    - @task: 包装为 Task
    - cache_key_fn: 缓存键生成
    - retry_delay_seconds: 重试延迟
    - timeout_seconds: 超时控制

    Args:
        name: Agent 名称
        execute_fn: 执行函数 (sandbox, input_data, context) -> AgentResult
        config: Agent 配置

    Returns:
        Prefect Task 函数
    """
    agent_config = config or AgentConfig(name=name)

    @task(
        name=name,
        description=f"Agent Task: {name}",
        timeout_seconds=300,
        retry_delay_seconds=5.0,
        cache_expiration="1d",  # Prefect 内置缓存过期
    )
    def agent_task(
        sandbox_path: str,
        input_data: Any,
        previous_results: Dict[str, AgentResult],
    ) -> AgentResult:
        """Agent Task"""
        from src.sandbox.filesystem import FilesystemSandbox
        from src.core.agent import AgentContext

        # 创建沙箱实例
        sandbox = FilesystemSandbox()

        # 创建上下文
        context = AgentContext(
            sandbox_path=sandbox_path,
            input_data=input_data,
            previous_results=previous_results or {},
        )

        try:
            # 执行智能体
            result = execute_fn(sandbox, input_data, context)

            # 如果执行失败，Prefect 会自动重试
            return result
        except Exception as e:
            return AgentResult(
                state=AgentState.FAILED,
                error=str(e),
            )

    return agent_task
