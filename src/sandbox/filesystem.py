"""文件系统沙箱实现"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional
from src.core.sandbox import BaseSandbox, SandboxConfig, compute_file_hash


class FilesystemSandbox(BaseSandbox):
    """文件系统沙箱 - 适用于代码仓库场景"""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.current_path: Optional[str] = None

    def setup(self, source_data: Any) -> str:
        """设置沙箱环境

        Args:
            source_data: 可以是:
                - Git URL (str): 克隆仓库
                - 本地路径 (str): 复制目录
                - 字典: 包含 repo_url 和其他信息
        """
        import tempfile

        # 生成唯一目录名
        import uuid
        run_id = uuid.uuid4().hex[:8]
        sandbox_path = Path(self.config.base_path) / f"sandbox_{run_id}"
        sandbox_path.mkdir(parents=True, exist_ok=True)

        self.current_path = str(sandbox_path)

        # 根据 source_data 类型处理
        if isinstance(source_data, str):
            if source_data.startswith("http") or source_data.endswith(".git"):
                # Git 仓库
                self._clone_repo(source_data, sandbox_path)
            else:
                # 本地目录
                self._copy_dir(source_data, sandbox_path)
        elif isinstance(source_data, dict):
            # 字典格式，如 {"repo_url": "...", "ref": "..."}
            repo_url = source_data.get("repo_url")
            if repo_url:
                self._clone_repo(repo_url, sandbox_path, ref=source_data.get("ref"))

        return self.current_path

    def _clone_repo(self, repo_url: str, target_path: Path, ref: Optional[str] = None):
        """克隆 Git 仓库"""
        cmd = ["git", "clone", "--depth", "1"]
        if ref:
            cmd.extend(["--branch", ref])
        cmd.extend([repo_url, str(target_path)])

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repo: {e}")

    def _copy_dir(self, source: str, target: Path):
        """复制本地目录"""
        src_path = Path(source)
        if not src_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source}")

        for item in src_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(src_path)
                dst_path = target / rel_path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst_path)

    def teardown(self, path: str):
        """清理沙箱环境"""
        if path and self.config.auto_cleanup:
            p = Path(path)
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
        self.current_path = None

    def get_file_hash(self, file_path: str) -> str:
        """获取文件哈希值"""
        full_path = file_path
        if not Path(file_path).is_absolute():
            if self.current_path:
                full_path = str(Path(self.current_path) / file_path)
        return compute_file_hash(full_path)

    def execute(self, command: str, timeout: Optional[int] = None, **kwargs) -> tuple:
        """在沙箱中执行命令"""
        if not self.current_path:
            raise RuntimeError("Sandbox not initialized")

        timeout = timeout or self.config.timeout_seconds

        result = subprocess.run(
            command,
            shell=True,
            cwd=self.current_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs
        )

        return result.returncode, result.stdout, result.stderr

    def read_file(self, relative_path: str) -> str:
        """读取沙箱中的文件"""
        if not self.current_path:
            raise RuntimeError("Sandbox not initialized")

        full_path = Path(self.current_path) / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        return full_path.read_text()

    def write_file(self, relative_path: str, content: str):
        """写入文件到沙箱"""
        if not self.current_path:
            raise RuntimeError("Sandbox not initialized")

        full_path = Path(self.current_path) / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    def list_files(self, pattern: str = "*") -> list:
        """列出沙箱中的文件"""
        if not self.current_path:
            raise RuntimeError("Sandbox not initialized")

        path = Path(self.current_path)
        return [str(p.relative_to(path)) for p in path.rglob(pattern) if p.is_file()]
