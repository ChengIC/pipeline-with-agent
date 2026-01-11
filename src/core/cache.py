"""缓存键生成函数 - 供 Prefect @task(cache_key_fn=...) 使用"""
import hashlib
import json
from typing import Any, Dict, Callable


def generate_cache_key(
    task_name: str,
    flow_run_id: str,
    input_data: Any,
    agent_config: Dict[str, Any]
) -> str:
    """生成 Prefect 缓存键

    Prefect 会自动调用此函数生成缓存标识
    """
    key_data = {
        "task": task_name,
        "flow_run": flow_run_id,
        "input": str(input_data) if not isinstance(input_data, (dict, list)) else input_data,
        "config": agent_config
    }
    content = json.dumps(key_data, sort_keys=True, default=str)
    return f"{task_name}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def sandbox_cache_key(task_run_context) -> str:
    """基于沙箱输入生成缓存键

    用作 @task(cache_key_fn=sandbox_cache_key)
    """
    from prefect.context import FlowRunContext

    flow_ctx = FlowRunContext.get()
    inputs = task_run_context.task.inputs

    # 使用输入的哈希值作为缓存键
    input_data = inputs.get("sandbox_input", {})
    if hasattr(input_data, 'value'):
        data = input_data.value
    else:
        data = input_data

    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def agent_cache_key_factory(agent_name: str, config: Dict[str, Any]) -> Callable:
    """创建 Agent 专用的缓存键工厂函数

    Usage:
        @task(cache_key_fn=agent_cache_key_factory("test_agent", {"version": "1.0"}))
        def test_agent(...):
            ...
    """
    def cache_key_fn(task_run_context) -> str:
        inputs = task_run_context.task.inputs
        input_data = inputs.get("input_data", {})
        if hasattr(input_data, 'value'):
            data = input_data.value
        else:
            data = input_data

        key_data = {
            "agent": agent_name,
            "config": config,
            "input": data
        }
        content = json.dumps(key_data, sort_keys=True, default=str)
        return f"{agent_name}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

    return cache_key_fn
