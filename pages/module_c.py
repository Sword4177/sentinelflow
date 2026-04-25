"""
sentinelflow/pages/module_c.py
─────────────────────────────────────────────────────────
Module C — 法律合规风险雷达

卡片按 HIGH → MOD → LOW 排序，左右两栏交错排列。
─────────────────────────────────────────────────────────
"""
import logging

import streamlit as st

from data.compliance import RISK_ORDER, ComplianceEntry, get_compliance_data

logger = logging.getLogger(__name__)

# 风险色阶 → (徽章文字, 颜色值) 查表
_BADGE_MAP: dict[str, tuple[str, str]] = {
    "high": ("🔴 HIGH RISK",     "#f85149"),
    "mod":  ("🟡 MODERATE RISK", "#e3b341"),
    "low":  ("🟢 LOW RISK",      "#21e786"),
}

# 生产前必检清单 — 纯数据，不含任何渲染逻辑
_REQUIRED_ACTIONS: dict[str, str] = {
    "☐ Seeking Alpha": (
        "Obtain data licensing agreement OR exclude from commercial product entirely."
    ),
    "☐ Reddit": (
        "Review Data API commercial terms if derived sentiment signals will be sold or licensed."
    ),
    "☐ Twitter/X": (
        "Ensure 30-day data retention limit compliance on Basic tier."
    ),
    "☐ Xueqiu / Weibo": (
        "Confirm internal-only use. Do not redistribute raw data commercially."
    ),
    "☐ All Sources": (
        "Implement rate limiting and request throttling to avoid ToS violations from abuse patterns."
    ),
}


def _render_risk_card(entry: ComplianceEntry) -> None:
    """
    渲染单个数据源的合规风险卡片（私有函数，只被 render_module_c 调用）。

    Args:
        entry: 单条 ComplianceEntry 合规记录。
    """
    badge_text, badge_color = _BADGE_MAP.get(
        entry["color"], ("◆ UNKNOWN", "#8b949e")
    )
    st.markdown(
        f"""
<div class="risk-{entry['color']}">
    <div class="risk-label" style="color:{badge_color};">{badge_text}</div>
    <div class="risk-source">{entry['source']}</div>
    <div class="risk-note">
        <strong style="color:#8b949e;">ToS:</strong> {entry['tos_clause']}<br/>
        <strong style="color:#8b949e;">Note:</strong> {entry['note']}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_module_c() -> None:
    """
    渲染 Module C：法律风险雷达面板 + 生产前合规检查清单。

    降级策略:
        ``get_compliance_data()`` 返回空列表时，
        所有风险计数为 0，卡片区域为空，不崩溃。
    """
    try:
        st.markdown(
            '<div class="section-label">▸ LEGAL RISK RADAR — ALL SOURCES</div>',
            unsafe_allow_html=True,
        )

        compliance = get_compliance_data()
        high_count = sum(1 for c in compliance if c["risk"] == "HIGH")
        mod_count  = sum(1 for c in compliance if "MOD" in c["risk"])
        low_count  = sum(1 for c in compliance if c["risk"] == "LOW")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("🔴 HIGH RISK",     high_count, delta="Legal action risk",  delta_color="inverse")
        r2.metric("🟡 MODERATE RISK", mod_count,  delta="ToS gray area",      delta_color="off")
        r3.metric("🟢 LOW RISK",      low_count,  delta="Cleared for use")
        r4.metric("SOURCES AUDITED",  len(compliance), delta="All mapped")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        sorted_compliance = sorted(
            compliance, key=lambda x: RISK_ORDER.get(x["risk"], 1)
        )

        col_left, col_right = st.columns(2)
        for i, entry in enumerate(sorted_compliance):
            with (col_left if i % 2 == 0 else col_right):
                _render_risk_card(entry)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">▸ REQUIRED ACTIONS BEFORE PRODUCTION</div>',
            unsafe_allow_html=True,
        )

        for action, detail in _REQUIRED_ACTIONS.items():
            st.markdown(
                f"""
<div style="font-family: 'Courier New', monospace; font-size: 0.73rem;
            background: #0d1117; border: 1px solid #21263a;
            border-radius: 3px; padding: 8px 14px; margin-bottom: 6px;">
    <strong style="color:#c9d1d9;">{action}</strong>
    <span style="color:#8b949e;"> — {detail}</span>
</div>
""",
                unsafe_allow_html=True,
            )

    except Exception as exc:
        logger.error("Module C 渲染失败: %s", exc, exc_info=True)
        st.error("⚠ Module C 加载异常，请检查日志或刷新页面。")
