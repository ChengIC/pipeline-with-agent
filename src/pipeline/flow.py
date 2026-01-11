"""Pipeline 编排 - 充分利用 Prefect Flow"""
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from src.core.agent import AgentResult
from src.sandbox.filesystem import FilesystemSandbox


@dataclass
class PipelineConfig:
    """流水线配置 - 直接映射 Prefect 参数"""
    name: str
    agents: List[Callable]  # Agent Task 列表
    sandbox_type: str = "filesystem"
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    timeout_seconds: int = 3600
    concurrency: int = 1  # 1=串行, N=并行
    cache_enabled: bool = True
    cache_expiration: str = "1d"  # Prefect 缓存过期时间


def create_pipeline(config: PipelineConfig) -> Callable:
    """创建 Prefect Flow 的工厂函数

    利用 Prefect 的:
    - cache_key_fn: 缓存键生成
    - retry_delay_seconds: 重试延迟
    - timeout_seconds: 超时控制
    - task_runner: 并发控制

    Args:
        config: Pipeline 配置

    Returns:
        Prefect Flow 函数
    """
    # 选择 Task Runner
    if config.concurrency == 1:
        runner = SequentialTaskRunner()
    else:
        runner = ConcurrentTaskRunner(max_workers=config.concurrency)

    @flow(
        name=config.name,
        task_runner=runner,
        timeout_seconds=config.timeout_seconds,
        description=f"Agent Pipeline: {config.name}",
        retries=config.max_retries,
        retry_delay_seconds=config.retry_delay_seconds,
    )
    def pipeline_flow(
        sandbox_input: Any,
        agent_configs: Optional[List[Dict]] = None,
    ) -> Dict[str, AgentResult]:
        """流水线 Flow - 串行或并行执行智能体

        Args:
            sandbox_input: 沙箱输入数据（如 Git URL）
            agent_configs: 可选的 Agent 配置列表

        Returns:
            每个 Agent 的执行结果
        """
        results = {}

        # 初始化沙箱
        sandbox = FilesystemSandbox()
        sandbox_path = sandbox.setup(sandbox_input)

        try:
            # 执行每个 Agent
            for i, agent in enumerate(config.agents):
                agent_config = (agent_configs[i] if agent_configs else {})

                result = agent(
                    sandbox_path=sandbox_path,
                    input_data=sandbox_input,
                    previous_results=results,
                )
                results[agent.name] = result

            return results

        finally:
            # 清理沙箱
            sandbox.teardown(sandbox_path)

    return pipeline_flow


def create_conditional_pipeline(
    config: PipelineConfig,
    continue_condition: Callable[[AgentResult], bool] = None
) -> Callable:
    """创建带条件分支的 Pipeline

    Args:
        config: Pipeline 配置
        continue_condition: 继续条件函数

    Returns:
        Prefect Flow 函数
    """
    # 选择 Task Runner
    if config.concurrency == 1:
        runner = SequentialTaskRunner()
    else:
        runner = ConcurrentTaskRunner(max_workers=config.concurrency)

    @flow(
        name=f"{config.name}-conditional",
        task_runner=runner,
        timeout_seconds=config.timeout_seconds,
    )
    def conditional_pipeline(
        sandbox_input: Any,
    ) -> Dict[str, AgentResult]:
        """条件流水线 - 根据结果决定是否继续"""
        results = {}

        # 初始化沙箱
        sandbox = FilesystemSandbox()
        sandbox_path = sandbox.setup(sandbox_input)

        try:
            for agent in config.agents:
                result = agent(
                    sandbox_path=sandbox_path,
                    input_data=sandbox_input,
                    previous_results=results,
                )
                results[agent.name] = result

                # 检查继续条件
                if continue_condition and not continue_condition(result):
                    break

            return results

        finally:
            sandbox.teardown(sandbox_path)

    return conditional_pipeline
