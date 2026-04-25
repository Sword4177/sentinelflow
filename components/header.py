"""
sentinelflow/components/header.py
─────────────────────────────────────────────────────────
顶部状态栏组件

所有展示文本从 AppConfig 读取，无硬编码字符串。
─────────────────────────────────────────────────────────
"""
import logging
from datetime import datetime

import streamlit as st

from config import APP_CONFIG, AppConfig

logger = logging.getLogger(__name__)


def render_header(cfg: AppConfig | None = None) -> None:
    """
    渲染顶部 Bloomberg 风格状态栏。

    Args:
        cfg: 应用配置实例。为 None 时使用全局 APP_CONFIG。

    降级策略:
        渲染失败时显示 st.error 内联错误提示，不中断页面其余部分。
    """
    if cfg is None:
        cfg = APP_CONFIG

    try:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        st.markdown(
            f"""
<div class="sentinel-header">
    <p class="sentinel-title">📡 {cfg.app_name}</p>
    <p class="sentinel-sub">
        {cfg.app_subtitle} &nbsp;|&nbsp; {now_str} &nbsp;|&nbsp;
        <span class="dot-green">●</span> LIVE &nbsp;
        <span class="dot-green">●</span> {cfg.sources_active} SOURCES ACTIVE &nbsp;
        <span class="dot-red">●</span> {cfg.sources_paused} PAUSED
    </p>
</div>
""",
            unsafe_allow_html=True,
        )
    except Exception as exc:
        logger.error("Header 渲染失败: %s", exc, exc_info=True)
        st.error("⚠ 系统状态栏渲染异常，请检查日志")
