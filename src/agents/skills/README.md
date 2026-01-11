# 自定义 Skills 注册

在此目录下添加自定义 Skills，每个 Skill 是一个 prompt 模板。

## Skill 定义示例

```python
# my_skill.py
from src.core.agent import register_skill

# 注册 Skill
register_skill(
    name="analyze_code",
    prompt="""You are a code analyst. Analyze the following code and provide:
1. Summary of functionality
2. Potential bugs
3. Performance considerations

Code: {code}
"""
)
```

## 使用方式

在 Agent 配置中指定 Skills：

```python
from src.agents.claude_agent import ClaudeAgent

agent = ClaudeAgent(
    name="my-agent",
    config={
        "skills": ["analyze_code"]
    }
)
```
