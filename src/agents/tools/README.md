# 自定义工具注册

在此目录下添加自定义工具，每个工具是一个 Python 函数。

## 工具定义示例

```python
# my_tool.py
from src.core.agent import register_tool

def my_custom_tool(sandbox, input_data, context):
    """自定义工具实现"""
    # 访问沙箱: context.sandbox_path
    # 访问输入: input_data
    # 访问之前结果: context.previous_results
    return {"result": "..."}

# 注册工具
register_tool("my_tool", my_custom_tool)
```

## 使用方式

在创建 Agent 时传入工具列表：

```python
from src.agents.claude_agent import create_claude_agent_task

my_task = create_claude_agent_task(
    name="my-agent",
    system_prompt="Use my_custom_tool to help you.",
)
```
