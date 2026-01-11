"""条件分支模块"""
from typing import Callable, Any
from src.core.agent import AgentState, AgentResult


# 预定义条件函数
def always_continue(result: AgentResult) -> bool:
    """总是继续"""
    return True


def stop_on_failure(result: AgentResult) -> bool:
    """失败时停止"""
    return result.state != AgentState.FAILED


def stop_on_success(result: AgentResult) -> bool:
    """成功时停止"""
    return result.state == AgentState.COMPLETED


def custom_condition(condition_fn: Callable[[AgentResult], bool]) -> Callable:
    """自定义条件包装器

    Usage:
        @flow
        def pipeline():
            result1 = agent1(...)
            if custom_condition(lambda r: r.metrics.get("score", 0) > 0.8)(result1):
                result2 = agent2(...)
    """
    return condition_fn
