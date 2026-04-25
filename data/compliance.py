"""
sentinelflow/data/compliance.py
─────────────────────────────────────────────────────────
合规风险数据层

各渠道 ToS 风险评级与合规注记。
RISK_ORDER 常量供 Module C 排序使用，与渲染逻辑解耦。
─────────────────────────────────────────────────────────
"""
import logging
from typing import TypedDict

import streamlit as st

logger = logging.getLogger(__name__)


class ComplianceEntry(TypedDict):
    """单个数据源的合规风险记录。"""
    source:     str  # 数据源名称
    risk:       str  # "HIGH" | "MODERATE" | "LOW-MOD" | "LOW"
    color:      str  # CSS 类后缀："high" | "mod" | "low"
    tos_clause: str  # ToS 具体条款摘要
    note:       str  # 实践层面的合规建议


# 风险排序权重 — 供外部 sorted() 调用，不在数据层做排序（单一职责）
RISK_ORDER: dict[str, int] = {
    "HIGH":     0,
    "MODERATE": 1,
    "LOW-MOD":  1,
    "LOW":      2,
}

_COMPLIANCE_RECORDS: list[ComplianceEntry] = [
    {
        "source": "Seeking Alpha", "risk": "HIGH", "color": "high",
        "tos_clause": "§4: prohibits robots/spiders, reproduction of content, commercial use without license.",
        "note": "DMCA takedowns issued to data vendors. Do not scrape article bodies for commercial use.",
    },
    {
        "source": "Reddit", "risk": "MODERATE", "color": "mod",
        "tos_clause": "§4(d): prohibits ML/AI training on data without commercial agreement.",
        "note": "Internal sentiment analysis tolerated. Reselling derived signals requires Data API agreement (~$12-24k/yr).",
    },
    {
        "source": "X / Twitter", "risk": "MODERATE", "color": "mod",
        "tos_clause": "Developer Agreement: prohibits bulk redistribution, 30-day storage limit on Basic tier.",
        "note": "Internal sentiment use compliant. Publishing raw tweets or building tweet archive is not.",
    },
    {
        "source": "Xueqiu 雪球", "risk": "LOW-MOD", "color": "mod",
        "tos_clause": "User Agreement: 不得使用爬虫等自动化工具抓取平台数据.",
        "note": "No known enforcement against researchers. Commercial redistribution carries higher risk.",
    },
    {
        "source": "Weibo", "risk": "LOW-MOD", "color": "mod",
        "tos_clause": "Open Platform Terms: third-party API access prohibited outside official partnerships (closed 2021).",
        "note": "Cookie scraping in legal gray area under CN Unfair Competition Law. Research use generally unenforced.",
    },
    {
        "source": "Eastmoney Guba", "risk": "LOW", "color": "low",
        "tos_clause": "No explicit anti-scraping clause in public terms.",
        "note": "No known enforcement actions. Commercial redistribution riskier under CN Data Security Law (DSL 2021).",
    },
    {
        "source": "Telegram", "risk": "LOW", "color": "low",
        "tos_clause": "ToS permit API access for personal and developer use via official credentials.",
        "note": "Telethon (MTProto) explicitly supported. Content copyright rests with channel operators.",
    },
    {
        "source": "ApeWisdom", "risk": "LOW", "color": "low",
        "tos_clause": "No published ToS restricting API access.",
        "note": "Free tier API usage unrestricted. No data licensing concerns for internal use.",
    },
    {
        "source": "StockTwits", "risk": "LOW", "color": "low",
        "tos_clause": "Developer agreement permits application development on free tier.",
        "note": "Commercial productization of derived sentiment signals requires data licensing review.",
    },
]


@st.cache_data
def get_compliance_data() -> list[ComplianceEntry]:
    """
    返回所有数据源的合规风险评估列表。

    降级策略:
        构建失败时返回空列表，Module C 页面的风险计数将显示 0，
        卡片区域为空，但不会崩溃或白屏。

    Returns:
        ComplianceEntry 列表（未排序，排序由调用方决定）。
    """
    try:
        logger.debug("合规数据加载完成，共 %d 条记录", len(_COMPLIANCE_RECORDS))
        return list(_COMPLIANCE_RECORDS)  # 返回副本，防止调用方修改原始数据
    except Exception as exc:
        logger.error("合规数据加载失败，返回空列表: %s", exc, exc_info=True)
        return []
