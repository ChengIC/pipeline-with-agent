"""MR 测试生成器示例

演示如何使用 Agent Pipeline 系统：
1. 克隆代码仓库（原始数据）
2. 生成单元测试
3. 验证测试（fail-to-pass 检测）
4. 根据反馈迭代

原始数据：Git 仓库的 MR（通过 git diff 生成）
沙箱环境：文件系统沙箱
智能体：A=测试生成器, B=测试验证器, C=迭代器
"""
from typing import Any, Dict
from src.core.agent import AgentState, AgentResult, AgentContext
from src.sandbox.filesystem import FilesystemSandbox
from src.agents.claude_agent import create_claude_agent_task
from src.pipeline import PipelineConfig, create_pipeline, create_conditional_pipeline


# ============== Agent Task 定义 ==============

# Agent 1: 克隆仓库
clone_repo_task = create_claude_agent_task(
    name="clone-repo",
    system_prompt="""You are a DevOps assistant. Your task is to prepare a sandbox environment.
Given a git repository URL, ensure it's cloned to the sandbox path.
Return the path where the repository is cloned.""",
)


# Agent 2: 生成单元测试
generate_test_task = create_claude_agent_task(
    name="generate-test",
    system_prompt="""You are a test generation expert. Given code in the sandbox,
generate comprehensive unit tests using pytest.

Instructions:
1. Read the code files to understand the functionality
2. Identify key functions/classes that need testing
3. Generate test cases with meaningful assertions
4. Output the test file(s) to the sandbox

Focus on edge cases and typical usage patterns.""",
)


# Agent 3: 验证测试（fail-to-pass 检测）
validate_test_task = create_claude_agent_task(
    name="validate-test",
    system_prompt="""You are a testing expert. Your task is to verify if the generated tests
correctly detect changes between before and after code.

Given:
- Before code (original)
- After code (modified)
- Generated tests

Determine:
1. Run tests on BEFORE code - expected to FAIL (tests detect the issue)
2. Run tests on AFTER code - expected to PASS (fix works)
3. Classify as:
   - "fail-to-pass": Tests fail before fix, pass after fix (GOOD)
   - "pass-to-pass": Tests pass both before and after (need improvement)
   - "pass-to-fail": Tests pass before, fail after (regression detected)

Return a detailed report with classification.""",
)


# Agent 4: 迭代优化（当测试质量不佳时）
iterate_task = create_claude_agent_task(
    name="iterate-test",
    system_prompt="""You are a test improvement expert. The previous test generation had issues.

Given the validation report, improve the tests:
- If "pass-to-pass": Create tests that specifically catch the issue
- If "pass-to-fail": Fix the regression
- If "fail-to-pass": Add more comprehensive edge case tests

Return improved test code.""",
)


# ============== 自定义执行函数示例 ==============

def execute_test_generation(
    sandbox: FilesystemSandbox,
    input_data: Any,
    context: AgentContext
) -> AgentResult:
    """自定义测试生成执行逻辑

    如果需要更精细的控制，可以定义完整的执行函数
    """
    import subprocess

    # 读取代码文件
    code_files = sandbox.list_files("*.py")

    # 生成测试
    test_content = []
    for cf in code_files[:5]:  # 限制文件数
        content = sandbox.read_file(cf)
        test_content.append(f"# File: {cf}\n{content[:500]}")

    prompt = f"""Generate pytest unit tests for these files:

{chr(10).join(test_content)}

Focus on the main functionality and edge cases."""

    # 这里可以调用实际的 LLM
    # 简化起见，返回模拟结果
    return AgentResult(
        state=AgentState.COMPLETED,
        output="Generated tests for files",
        metrics={"files_processed": len(code_files)},
    )


# ============== Pipeline 创建 ==============

def create_mr_test_pipeline(
    concurrency: int = 1,
    cache_enabled: bool = True,
) -> callable:
    """创建 MR 测试生成 Pipeline

    Args:
        concurrency: 并发数（1=串行, N=并行处理多个MR）
        cache_enabled: 是否启用缓存

    Returns:
        Prefect Flow 函数
    """
    config = PipelineConfig(
        name="mr-test-generator",
        agents=[
            clone_repo_task,
            generate_test_task,
            validate_test_task,
            iterate_task,  # 仅在需要时执行
        ],
        concurrency=concurrency,
        cache_enabled=cache_enabled,
        cache_expiration="1d",
    )

    # 创建条件 Pipeline - 如果验证通过则跳过迭代
    def continue_only_if_needed(result: AgentResult) -> bool:
        if result.state != AgentState.COMPLETED:
            return True
        # 如果验证结果显示 pass-to-pass 比例高，则需要迭代
        metrics = result.metrics or {}
        if metrics.get("pass_to_pass_ratio", 0) > 0.5:
            return True
        return False

    return create_conditional_pipeline(config, continue_condition=continue_only_if_needed)


# ============== 快速使用 ==============

def run_mr_test(
    repo_url: str,
    concurrency: int = 1,
) -> Dict[str, AgentResult]:
    """快速运行 MR 测试生成

    Args:
        repo_url: Git 仓库 URL
        concurrency: 并发数

    Returns:
        各 Agent 的执行结果
    """
    pipeline = create_mr_test_pipeline(concurrency=concurrency)

    result = pipeline(sandbox_input=repo_url)
    return result


# ============== 演示 ==============

if __name__ == "__main__":
    # 方式1: 快速运行
    results = run_mr_test(
        repo_url="https://github.com/example/repo.git",
        concurrency=1,
    )

    # 方式2: 自定义 Pipeline
    from src.pipeline import PipelineConfig, create_pipeline

    custom_config = PipelineConfig(
        name="custom-pipeline",
        agents=[clone_repo_task, generate_test_task],
        concurrency=1,
    )
    pipeline = create_pipeline(custom_config)

    results = pipeline(sandbox_input="https://github.com/anthropics/claude-code.git")

    print("Pipeline Results:")
    for name, result in results.items():
        print(f"  {name}: {result.state.value}")
