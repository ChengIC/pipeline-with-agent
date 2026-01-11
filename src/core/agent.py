"""核心 Agent 模块 - 数据类和注册表"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable
from enum import Enum


class AgentState(Enum):
    """智能体状态 - 对齐 Prefect State"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentResult:
    """智能体执行结果"""
    state: AgentState
    output: Any = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    cache_key: Optional[str] = None


@dataclass
class AgentContext:
    """智能体执行上下文"""
    sandbox_path: str
    input_data: Any
    previous_results: Dict[str, "AgentResult"] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# 工具/Skills 注册表（用户自定义）
TOOL_REGISTRY: Dict[str, Callable] = {}
SKILL_REGISTRY: Dict[str, str] = {}


def register_tool(name: str, func: Callable):
    """注册工具函数

    Args:
        name: 工具名称
        func: 工具处理函数
    """
    TOOL_REGISTRY[name] = func


def register_skill(name: str, prompt: str):
    """注册 Skill

    Args:
        name: Skill 名称
        prompt: Skill prompt 模板
    """
    SKILL_REGISTRY[name] = prompt


def get_tool(name: str) -> Optional[Callable]:
    """获取已注册的工具"""
    return TOOL_REGISTRY.get(name)


def get_skill(name: str) -> Optional[str]:
    """获取已注册的 Skill"""
    return SKILL_REGISTRY.get(name)


def list_tools() -> list:
    """列出所有已注册的工具"""
    return list(TOOL_REGISTRY.keys())


def list_skills() -> list:
    """列出所有已注册的 Skills"""
    return list(SKILL_REGISTRY.keys())
