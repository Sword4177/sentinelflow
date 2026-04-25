"""
sentinelflow/pages/module_a.py
─────────────────────────────────────────────────────────
Module A — 实时行情图表 + 舆情 Feed 面板

布局：控制栏（Ticker / 周期 / 过滤器）+ 7:3 分栏（图表 | Feed）
─────────────────────────────────────────────────────────
"""
import logging
from datetime import datetime

import streamlit as st

from components.feed_card import render_feed_card
from components.tradingview import build_tradingview_widget
from config import APP_CONFIG
from data.feed import FeedEntry, get_feed_data

logger = logging.getLogger(__name__)

_FILTER_OPTIONS:   list[str] = ["ALL", "BULL", "BEAR", "NEUT"]
_INTERVAL_OPTIONS: list[str] = ["1", "5", "15", "60", "D"]


def _filter_feed(feed: list[FeedEntry], filter_val: str) -> list[FeedEntry]:
    """按情绪标签过滤 Feed 列表。filter_val="ALL" 时返回全量。"""
    if filter_val == "ALL":
        return feed
    return [e for e in feed if e["sentiment"] == filter_val]


def _render_feed_metrics(feed: list[FeedEntry]) -> None:
    """渲染 Bull / Bear / Total 信号计数 Metric 卡片行。"""
    total = len(feed)
    bulls = sum(1 for e in feed if e["sentiment"] == "BULL")
    bears = sum(1 for e in feed if e["sentiment"] == "BEAR")

    m1, m2, m3 = st.columns(3)
    m1.metric("SIGNALS", total)
    m2.metric("▲ BULL", bulls, delta=f"+{bulls}")
    m3.metric("▼ BEAR", bears, delta=f"-{bears}", delta_color="inverse")


def _render_scrollable_feed(feed: list[FeedEntry]) -> None:
    """
    渲染带竖向滚动条的舆情 Feed 容器。

    Feed 通过 st.components.v1.html() 渲染，内部是独立 iframe，
    父页面的全局 CSS 无法穿透 iframe 边界。
    因此必须将所有 feed-card 样式直接内嵌进此函数的 HTML 字符串中。
    """
    cfg = APP_CONFIG
    c = cfg.theme
    feed_html = "".join(render_feed_card(e) for e in feed)

    # 内嵌 CSS：与 styles.py 的 feed-card 规则保持同步
    inline_css = f"""
<style>
  body {{ margin: 0; background: {c.bg_primary}; }}
  .feed-card {{
    background: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-left: 3px solid {c.accent_green};
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-family: 'Courier New', monospace;
    font-size: 0.72rem;
  }}
  .feed-card.bearish {{ border-left-color: {c.accent_red}; }}
  .feed-card.neutral {{ border-left-color: {c.accent_blue}; }}
  .feed-source {{ color: {c.accent_blue}; font-size: 0.65rem; letter-spacing: 1px; }}
  .feed-time   {{ color: {c.text_dim}; font-size: 0.62rem; float: right; }}
  .feed-text   {{ color: {c.text_primary}; margin-top: 3px; line-height: 1.4; }}
  .feed-tag-bull {{ color: {c.accent_green}; font-weight: 700; }}
  .feed-tag-bear {{ color: {c.accent_red}; font-weight: 700; }}
  .feed-tag-neu  {{ color: {c.accent_blue}; font-weight: 700; }}
</style>
"""

    st.components.v1.html(
        f"""
        {inline_css}
        <div style="
            height: {cfg.layout.feed_scroll_height}px;
            overflow-y: auto;
            background: {c.bg_primary};
            padding: 4px;
            scrollbar-width: thin;
            scrollbar-color: {c.accent_green} {c.bg_primary};
        ">
            {feed_html}
        </div>
        """,
        height=cfg.layout.feed_component_height,
        scrolling=False,
    )


def render_module_a() -> None:
    """
    渲染 Module A 完整页面。

    降级策略:
        - Feed 数据获取失败时显示空状态，不抛出异常（由数据层保证）。
        - TradingView Widget 构建失败时显示内联错误提示（由组件层保证）。
        - 若整体渲染意外失败，捕获后显示 st.error，不白屏。
    """
    try:
        # ── 控制栏 ──
        col_sel1, col_sel2, col_sel3, _ = st.columns([1.2, 1.2, 1.2, 6.4])

        with col_sel1:
            ticker_input: str = st.selectbox(
                "TICKER",
                APP_CONFIG.available_tickers,
                index=0,
                label_visibility="visible",
            )
        with col_sel2:
            st.selectbox("INTERVAL", _INTERVAL_OPTIONS, index=2)
        with col_sel3:
            feed_filter: str = st.selectbox("FEED FILTER", _FILTER_OPTIONS, index=0)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── 主体：图表 | Feed ──
        col_chart, col_feed = st.columns([7, 3])

        with col_chart:
            st.markdown(
                '<div class="section-label">▸ TRADINGVIEW ADVANCED CHART</div>',
                unsafe_allow_html=True,
            )
            chart_html = build_tradingview_widget(symbol=ticker_input)
            st.components.v1.html(
                chart_html,
                height=APP_CONFIG.layout.chart_component_height,
                scrolling=False,
            )

        with col_feed:
            st.markdown(
                '<div class="section-label">▸ LIVE SENTIMENT FEED</div>',
                unsafe_allow_html=True,
            )
            feed_data = _filter_feed(get_feed_data(), feed_filter)
            _render_feed_metrics(feed_data)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_scrollable_feed(feed_data)

        # ── 底部状态栏 ──
        now_str = datetime.utcnow().strftime("%H:%M:%S UTC")
        st.markdown(
            f"""
<div class="status-bar">
    ● LAST REFRESH: {now_str} &nbsp;|&nbsp;
    SOURCES POLLED: APEWISDOM · REDDIT · STOCKTWITS · GUBA · TELEGRAM &nbsp;|&nbsp;
    LATENCY: {APP_CONFIG.display_latency_avg} AVG
</div>
""",
            unsafe_allow_html=True,
        )

    except Exception as exc:
        logger.error("Module A 渲染失败: %s", exc, exc_info=True)
        st.error("⚠ Module A 加载异常，请检查日志或刷新页面。")
