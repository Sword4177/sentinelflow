"""
sentinelflow/pages/module_b.py
─────────────────────────────────────────────────────────
Module B — 数据源矩阵与实施路线图
─────────────────────────────────────────────────────────
"""
import logging

import streamlit as st

from data.sources import get_source_matrix

logger = logging.getLogger(__name__)

# 列配置抽为模块级常量，避免每次渲染重复构造
_COLUMN_CONFIG: dict = {
    "Tier": st.column_config.TextColumn(
        "TIER", width="small",
        help="🟢 Start here | 🟡 Medium effort | 🔴 Hard/risky",
    ),
    "Source":   st.column_config.TextColumn("SOURCE",               width="medium"),
    "Category": st.column_config.TextColumn("CATEGORY",             width="small"),
    "Language": st.column_config.TextColumn("LANG",                 width="small"),
    "API":      st.column_config.TextColumn(
        "API STATUS", width="small",
        help="✅ Official | ⚠️ Unofficial/Reverse-engineered | ❌ None/Prohibited",
    ),
    "Reason": st.column_config.TextColumn("ACQUISITION RATIONALE",  width="large"),
}

# (标签, 值, delta 文本, delta_color) 四元组列表
_VELOCITY_METRICS: list[tuple[str, str, str, str]] = [
    ("Tier 1 Sources", "5", "Ready now",      "normal"),
    ("Tier 2 Sources", "4", "1-2 weeks",       "normal"),
    ("Tier 3 Sources", "2", "Deprioritize",    "inverse"),
    ("Free Sources",   "7", "$0/mo baseline",  "normal"),
    ("Paid Required",  "1", "$100/mo Twitter", "normal"),
]


def render_module_b() -> None:
    """
    渲染 Module B：分层数据源采集路线图 + 实施速度估算。

    降级策略:
        ``get_source_matrix()`` 返回空 DataFrame 时，
        ``st.dataframe`` 显示空表，其余 Metric 卡片正常渲染。
    """
    try:
        st.markdown(
            '<div class="section-label">▸ TIERED DATA SOURCE ACQUISITION ROADMAP</div>',
            unsafe_allow_html=True,
        )

        df = get_source_matrix()
        st.dataframe(
            df,
            use_container_width=True,
            height=480,
            column_config=_COLUMN_CONFIG,
            hide_index=True,
        )

        st.markdown(
            """
<div style="font-family: 'Courier New', monospace; font-size: 0.68rem; color: #484f58;
            margin-top: 12px; border-top: 1px solid #21263a; padding-top: 8px;">
    LEGEND &nbsp;|&nbsp;
    🟢 TIER 1 — operational within 48hrs, free or low-cost &nbsp;|&nbsp;
    🟡 TIER 2 — requires infra setup or ongoing cost &nbsp;|&nbsp;
    🔴 TIER 3 — legal exposure or prohibitive engineering cost
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">▸ IMPLEMENTATION VELOCITY ESTIMATE</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(len(_VELOCITY_METRICS))
        for col, (label, value, delta, delta_color) in zip(cols, _VELOCITY_METRICS):
            col.metric(label, value, delta=delta, delta_color=delta_color)

    except Exception as exc:
        logger.error("Module B 渲染失败: %s", exc, exc_info=True)
        st.error("⚠ Module B 加载异常，请检查日志或刷新页面。")
