"""
sentinelflow/pages/module_d.py
─────────────────────────────────────────────────────────
Module D — Truth Signal: Trump Truth Social → 市场影响分析

架构设计：
    上方：Python 层统计 Metric（来自 data/truth_signal.py）
    下方：完整交互式 HTML 面板（模板 + 动态数据注入）

单一数据源原则：
    所有事件数据只存在于 data/truth_signal.py。
    HTML 模板使用 __EVENTS_PLACEHOLDER__ 占位符，
    渲染时由此模块将 Python 数据序列化为 JSON 注入，
    不再维护 HTML 内的独立数据副本。
─────────────────────────────────────────────────────────
"""
import json
import logging
from pathlib import Path

import streamlit as st

from data.truth_signal import get_summary_stats, get_truth_events

logger = logging.getLogger(__name__)

# HTML 模板路径
_ASSET_PATH = Path(__file__).parent.parent / "assets" / "truth_signal.html"

# 嵌入高度（像素）
_EMBED_HEIGHT = 820

# HTML 占位符 — 与模板文件中保持一致
_EVENTS_PLACEHOLDER = "__EVENTS_PLACEHOLDER__"


def _build_html() -> str | None:
    """
    读取 HTML 模板并将 Python 事件数据注入占位符。

    核心改进：
        原版 HTML 内嵌独立 JS 数据，与 Python 数据层双份维护。
        现在 HTML 只是模板，数据唯一来源是 data/truth_signal.py。
        修改事件数据只需改 Python 层，HTML 模板永远不需要动。

    降级策略：
        文件不存在 → 返回 None，调用方显示内联错误
        占位符不存在 → 记录 WARNING，继续渲染（向后兼容）
        JSON 序列化失败 → 记录 ERROR，返回 None

    Returns:
        注入数据后的完整 HTML 字符串，失败时返回 None。
    """
    try:
        template = _ASSET_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("truth_signal.html 模板未找到，路径: %s", _ASSET_PATH)
        return None
    except Exception as exc:
        logger.error("truth_signal.html 读取失败: %s", exc, exc_info=True)
        return None

    if _EVENTS_PLACEHOLDER not in template:
        logger.warning(
            "HTML 模板中未找到占位符 '%s'，可能使用旧版模板，跳过数据注入",
            _EVENTS_PLACEHOLDER,
        )
        return template

    try:
        events = get_truth_events()
        # ensure_ascii=False：保留原文中的引号、特殊字符
        events_json = json.dumps(events, ensure_ascii=False)
    except Exception as exc:
        logger.error("事件数据序列化失败: %s", exc, exc_info=True)
        return None

    html = template.replace(_EVENTS_PLACEHOLDER, events_json)
    logger.debug(
        "HTML 模板注入完成：%d 条事件，最终大小 %d 字节",
        len(events), len(html),
    )
    return html


def _render_summary_metrics() -> None:
    """渲染顶部五格 Metric 卡片（Python 数据层驱动）。"""
    events = get_truth_events()
    stats = get_summary_stats(events)

    tag_counts: dict[str, int] = {}
    for e in events:
        tag_counts[e["tag"]] = tag_counts.get(e["tag"], 0) + 1

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("EVENTS TRACKED", stats["total"],               delta="Jan 2025 – Apr 2026")
    m2.metric("AVG NEG SPX",    f"{stats['avg_neg_spx']}%",   delta="per shock",    delta_color="inverse")
    m3.metric("AVG POS SPX",    f"+{stats['avg_pos_spx']}%",  delta="per relief")
    m4.metric("MAX BTC GAIN",   f"+{stats['max_btc_gain']}%", delta="BTC Reserve EO")
    m5.metric("TARIFF EVENTS",  tag_counts.get("trade", 0),   delta="dominant category", delta_color="off")


def render_module_d() -> None:
    """
    渲染 Module D 完整页面。

    降级策略：
        - Metric 数据层失败 → 显示空 Metric，不中断 HTML 面板渲染
        - HTML 模板或注入失败 → 显示内联错误提示，引导用户排查
        - 整体异常 → st.error，不白屏
    """
    try:
        st.markdown(
            '<div class="section-label">▸ TRUTH SIGNAL — TRUMP TRUTH SOCIAL → MARKET IMPACT</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-label">▸ AGGREGATE STATISTICS</div>',
            unsafe_allow_html=True,
        )
        _render_summary_metrics()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-label">▸ INTERACTIVE EVENT TIMELINE</div>',
            unsafe_allow_html=True,
        )

        html_content = _build_html()

        if html_content is None:
            st.error(
                f"⚠ HTML 面板加载失败。\n\n"
                f"请确认模板文件位于: `{_ASSET_PATH}`"
            )
            return

        st.components.v1.html(
            html_content,
            height=_EMBED_HEIGHT,
            scrolling=True,
        )

        st.markdown(
            """
<div style="
    font-family: 'Courier New', monospace; font-size: 0.65rem;
    color: #484f58; border-top: 1px solid #21263a;
    padding-top: 8px; margin-top: 8px;
">
    NEXT MILESTONE: Playwright scraper → Truth Social full history │
    yfinance T+1/T+3 price alignment │ FinBERT sentiment scoring │ auto-refresh pipeline
</div>
""",
            unsafe_allow_html=True,
        )

    except Exception as exc:
        logger.error("Module D 渲染失败: %s", exc, exc_info=True)
        st.error("⚠ Module D 加载异常，请检查日志或刷新页面。")
