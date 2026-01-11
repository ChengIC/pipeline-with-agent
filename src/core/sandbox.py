"""核心 Sandbox 模块"""
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
import hashlib
import shutil


@dataclass
class SandboxConfig:
    """沙箱配置"""
    base_path: Path = Path("./sandbox")
    max_size_mb: int = 2048
    timeout_seconds: int = 300
    auto_cleanup: bool = True


class BaseSandbox(ABC):
    """沙箱环境基类"""

    @abstractmethod
    def setup(self, source_data: Any) -> str:
        """设置沙箱环境，返回沙箱路径"""
        pass

    @abstractmethod
    def teardown(self, path: str):
        """清理沙箱环境"""
        pass

    @abstractmethod
    def get_file_hash(self, file_path: str) -> str:
        """获取文件哈希值用于缓存键"""
        pass

    def execute(self, command: str, **kwargs):
        """在沙箱中执行命令"""
        pass


def compute_file_hash(file_path: str) -> str:
    """计算文件哈希值用于缓存键"""
    path = Path(file_path)
    if not path.exists():
        return ""

    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]


def compute_data_hash(data: Any) -> str:
    """计算数据哈希值"""
    import json
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()[:16]
