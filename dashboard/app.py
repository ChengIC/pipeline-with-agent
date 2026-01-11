"""Streamlit Dashboard - 连接 Prefect API 监控流水线"""
import streamlit as st
from pathlib import Path
import json
from datetime import datetime


class PipelineDashboard:
    """连接 Prefect 的 Dashboard"""

    def __init__(self, prefect_api_url: str = None):
        self.prefect_api_url = prefect_api_url or "http://127.0.0.1:4200"

    def run(self):
        """运行 Dashboard"""
        st.set_page_config(
            page_title="Agent Pipeline Monitor",
            layout="wide",
            page_icon="🤖"
        )

        # 侧边栏导航
        st.sidebar.title("🤖 Pipeline Monitor")

        # 页面选择
        page = st.sidebar.selectbox(
            "Navigation",
            ["Overview", "Flow Runs", "Task Details", "Artifacts", "Analytics"]
        )

        # 连接状态
        status = self._check_connection()
        st.sidebar.markdown("---")
        st.sidebar.info(f"Prefect API: {self.prefect_api_url}")
        st.sidebar.success(f"Status: {'Connected' if status else 'Local Mode'}")

        # 页面路由
        if page == "Overview":
            self._show_overview()
        elif page == "Flow Runs":
            self._show_flow_runs()
        elif page == "Task Details":
            self._show_task_details()
        elif page == "Artifacts":
            self._show_artifacts()
        elif page == "Analytics":
            self._show_analytics()

    def _check_connection(self) -> bool:
        """检查 Prefect 连接"""
        try:
            from prefect.client import PrefectClient
            client = PrefectClient()
            # 尝试获取 flow
            list(client.read_flows(limit=1))
            return True
        except Exception:
            return False

    def _show_overview(self):
        """总览页面"""
        st.title("📊 Pipeline Overview")

        # 关键指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Flows", "12", "+3")
        with col2:
            st.metric("Active Runs", "2", "-1")
        with col3:
            st.metric("Success Rate", "85%", "+5%")
        with col4:
            st.metric("Avg Duration", "2m 30s", "-30s")

        # 最近运行
        st.subheader("Recent Runs")
        st.info("Connect to Prefect API to see live data")

        # 快速启动
        st.subheader("Quick Start")
        with st.expander("Run MR Test Generator"):
            repo_url = st.text_input("Repository URL", "https://github.com/example/repo.git")
            concurrency = st.slider("Concurrency", 1, 10, 1)
            if st.button("Run Pipeline"):
                st.success(f"Starting pipeline for {repo_url}")
                # 这里可以调用实际的 pipeline

    def _show_flow_runs(self):
        """显示 Flow 运行状态"""
        st.title("📋 Flow Runs")

        # 过滤器
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Status",
                ["Completed", "Failed", "Running", "Pending"]
            )
        with col2:
            flow_filter = st.text_input("Flow Name")

        st.info("Connect to Prefect API to see live flow runs")

        # 示例数据展示
        st.subheader("Sample Data")
        sample_runs = [
            {"name": "mr-test-generator", "status": "Completed", "duration": "2m 30s"},
            {"name": "custom-pipeline", "status": "Running", "duration": "45s"},
            {"name": "mr-test-generator", "status": "Failed", "duration": "1m 15s"},
        ]
        st.table(sample_runs)

    def _show_task_details(self):
        """显示 Task 详情"""
        st.title("🔍 Task Details")

        task_name = st.text_input("Task Name", "generate-test")

        if st.button("Load Task"):
            st.subheader(f"Task: {task_name}")
            st.json({
                "name": task_name,
                "type": "Agent Task",
                "cache_expiration": "1d",
                "retry_delay": "5s",
                "timeout": "300s"
            })

    def _show_artifacts(self):
        """显示 Artifacts"""
        st.title("📦 Artifacts")

        st.info("Artifacts from agent runs will appear here")

        # 示例
        with st.expander("Sample Artifact"):
            st.code("""
{
    "type": "test-results",
    "content": {
        "pass_to_pass": 5,
        "fail_to_pass": 3,
        "pass_to_fail": 1
    }
}
            """)

    def _show_analytics(self):
        """数据分析"""
        st.title("📊 Analytics")

        # 图表
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Runs by Day")
            st.bar_chart({
                "Mon": 5,
                "Tue": 8,
                "Wed": 12,
                "Thu": 7,
                "Fri": 10,
            })

        with col2:
            st.subheader("Success Rate by Flow")
            st.bar_chart({
                "mr-test-generator": 0.85,
                "custom-pipeline": 0.92,
                "other-flow": 0.75,
            })

        # 趋势
        st.subheader("Duration Trend")
        st.line_chart([2.5, 2.3, 2.8, 2.1, 2.4, 2.2])


def main():
    """主入口"""
    dashboard = PipelineDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
