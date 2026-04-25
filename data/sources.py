"""
sentinelflow/data/sources.py
─────────────────────────────────────────────────────────
数据源采集路线图数据层

各渠道的分层评级、API 状态及获取理由。
修改数据只需编辑 _SOURCE_RECORDS，与渲染逻辑完全解耦。
─────────────────────────────────────────────────────────
"""
import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# 数据源原始记录 — 纯数据，零渲染逻辑
_SOURCE_RECORDS: list[dict[str, str]] = [
    # ── Tier 1：48 小时内可落地 ──
    {
        "Tier": "🟢 Tier 1", "Source": "ApeWisdom",
        "Category": "Aggregator", "Language": "EN", "API": "✅ REST",
        "Reason": "Free, no auth, pre-aggregated Reddit signal",
    },
    {
        "Tier": "🟢 Tier 1", "Source": "Reddit (PRAW)",
        "Category": "Social Forum", "Language": "EN", "API": "✅ Official",
        "Reason": "Official API, free, 60 req/min, 3 subreddits",
    },
    {
        "Tier": "🟢 Tier 1", "Source": "StockTwits",
        "Category": "Social Finance", "Language": "EN", "API": "✅ Official",
        "Reason": "Bullish/bearish ground-truth labels, 400 req/hr",
    },
    {
        "Tier": "🟢 Tier 1", "Source": "Eastmoney Guba",
        "Category": "Social Forum", "Language": "ZH", "API": "⚠️ Unofficial",
        "Reason": "No login required, A-share retail, requests only",
    },
    {
        "Tier": "🟢 Tier 1", "Source": "Telegram (智堡/WSC)",
        "Category": "Aggregator", "Language": "ZH/EN", "API": "✅ Telethon",
        "Reason": "Telethon MTProto, low volume, high editorial quality",
    },
    # ── Tier 2：需基础设施投入 ──
    {
        "Tier": "🟡 Tier 2", "Source": "Xueqiu 雪球",
        "Category": "Social Finance", "Language": "ZH", "API": "⚠️ Unofficial",
        "Reason": "Stable endpoints, needs mainland server + account rotation",
    },
    {
        "Tier": "🟡 Tier 2", "Source": "X/Twitter KOLs",
        "Category": "Macro KOL", "Language": "EN", "API": "✅ v2 Official",
        "Reason": "$100/mo, irreplaceable Fed/macro signal (@NickTimiraos)",
    },
    {
        "Tier": "🟡 Tier 2", "Source": "Weibo Finance KOLs",
        "Category": "Macro KOL", "Language": "ZH", "API": "⚠️ Unofficial",
        "Reason": "Cookie auth, mainland server needed, no equivalent source",
    },
    {
        "Tier": "🟡 Tier 2", "Source": "SwaggyStocks",
        "Category": "Aggregator", "Language": "EN", "API": "❌ Scrape only",
        "Reason": "Cloudflare blocks, Playwright needed, marginal over ApeWisdom",
    },
    # ── Tier 3：暂时降级 ──
    {
        "Tier": "🔴 Tier 3", "Source": "Seeking Alpha",
        "Category": "Professional", "Language": "EN", "API": "❌ Prohibited",
        "Reason": "ToS bans scraping, Cloudflare, paywall, legal risk",
    },
    {
        "Tier": "🔴 Tier 3", "Source": "Xiaohongshu 小红书",
        "Category": "Social Lifestyle", "Language": "ZH", "API": "❌ App-only",
        "Reason": "No stable API, device fingerprint, lowest signal/effort ratio",
    },
]


@st.cache_data
def get_source_matrix() -> pd.DataFrame:
    """
    返回数据源采集路线图 DataFrame。

    降级策略:
        DataFrame 构建失败时返回空 DataFrame，
        Streamlit ``st.dataframe`` 会显示空表而非抛出异常，
        Module B 页面仍可正常渲染其余组件。

    Returns:
        包含 Tier / Source / Category / Language / API / Reason 列的 DataFrame。
    """
    try:
        df = pd.DataFrame(_SOURCE_RECORDS)
        logger.debug("数据源矩阵加载完成，共 %d 行", len(df))
        return df
    except Exception as exc:
        logger.error("数据源矩阵构建失败，返回空 DataFrame: %s", exc, exc_info=True)
        return pd.DataFrame()
