"""
sentinelflow/data/feed.py
─────────────────────────────────────────────────────────
舆情 Feed 数据层

当前实现为 Mock 数据，接口设计与真实 API 同构：
替换真实数据源时，只需修改 _fetch_from_api() 内部，
get_feed_data() 的签名和返回类型保持不变。
─────────────────────────────────────────────────────────
"""
import logging
import random
from datetime import datetime, timedelta
from typing import TypedDict

import streamlit as st

from config import APP_CONFIG, FeedConfig

logger = logging.getLogger(__name__)


class FeedEntry(TypedDict):
    """
    单条舆情信号的数据结构。

    使用 TypedDict 而非 dict，使得 IDE 可以对键名做静态检查，
    同时比 dataclass 更轻量（无需实例化开销）。
    """
    source:    str   # 数据源名称，如 "REDDIT/WSB"
    tier:      str   # 分层标识，如 "T1"
    sentiment: str   # "BULL" | "BEAR" | "NEUT"
    text:      str   # 原始信号文本
    time:      str   # HH:MM:SS UTC 格式时间戳


# ──────────────────────────────────────────────
# 原始语料库 — 未来可替换为 API 响应解析
# ──────────────────────────────────────────────
_RAW_ENTRIES: list[tuple[str, str, str, str]] = [
    ("APEWISDOM", "T1", "BULL", "$NVDA mentions +340% in 1hr — WSB momentum spike"),
    ("REDDIT/WSB", "T1", "BULL", "YOLO earnings play $TSLA — 847 upvotes 2min"),
    ("STOCKTWITS", "T1", "BEAR", "$SPY puts loading. Fed minutes dropped bearish."),
    ("GUBA/东财",   "T1", "BULL", "贵州茅台主力资金净流入 ¥12.3亿 异常放量"),
    ("APEWISDOM", "T1", "BULL", "$AMD rank ↑ 47 positions — unusual mention surge"),
    ("REDDIT/INV", "T1", "BEAR", "Rate cut expectations collapsing — 10Y at 4.82%"),
    ("STOCKTWITS", "T1", "BULL", "$BTC breaking 98k — whale accumulation confirmed"),
    ("GUBA/东财",   "T1", "BEAR", "中概股集体跳水，纳指期货承压，情绪极度悲观"),
    ("TELEGRAM",   "T1", "NEUT", "智堡: 日央行政策会议纪要显示鸽派偏向未变"),
    ("REDDIT/STK", "T1", "BULL", "$INTC reversal pattern — support held at $21.4"),
    ("APEWISDOM", "T1", "BULL", "$GME reappearing on trending — volume confirming"),
    ("STOCKTWITS", "T1", "BEAR", "$META ad revenue miss — downgrade incoming"),
    ("GUBA/东财",   "T1", "NEUT", "沪深300窄幅震荡，成交量持续萎缩"),
    ("TELEGRAM",   "T1", "NEUT", "华尔街见闻: 美联储官员讲话偏鹰，市场定价调整"),
    ("REDDIT/WSB", "T1", "BULL", "Unusual options activity $PLTR 45C exp Friday"),
]


def _build_entries(
    raw: list[tuple[str, str, str, str]],
    cfg: FeedConfig,
    base_time: datetime,
) -> list[FeedEntry]:
    """
    将原始语料四元组列表转化为带时间戳的 FeedEntry 列表（私有工具函数）。

    使用下划线前缀表示不对外暴露，单独抽出便于单元测试（可以 mock base_time）。

    Args:
        raw:       原始 (source, tier, sentiment, text) 四元组列表。
        cfg:       Feed 时间戳配置。
        base_time: 时间戳生成基准时刻（UTC）。

    Returns:
        FeedEntry 列表，第 0 条为最新信号。
    """
    entries: list[FeedEntry] = []
    for i, (source, tier, sentiment, text) in enumerate(raw):
        jitter = random.randint(0, cfg.timestamp_jitter_max)
        offset = i * cfg.timestamp_base_interval + jitter
        ts = base_time - timedelta(seconds=offset)
        entries.append(
            FeedEntry(
                source=source,
                tier=tier,
                sentiment=sentiment,
                text=text,
                time=ts.strftime("%H:%M:%S"),
            )
        )
    return entries


@st.cache_data(ttl=60)
def get_feed_data() -> list[FeedEntry]:
    """
    获取多渠道舆情信号列表。

    当前实现为 Mock 数据；接口与真实 API 同构，替换时只改此函数内部。
    TTL=60s：避免频繁重渲染的同时保证数据相对新鲜。

    降级策略:
        构建过程中发生任何异常，返回空列表并记录 ERROR 日志，
        防止异常向 UI 层传播（UI 层将显示空 Feed，而非整页崩溃）。

    Returns:
        FeedEntry 列表，最新信号在前。
    """
    try:
        feed = _build_entries(_RAW_ENTRIES, APP_CONFIG.feed, datetime.utcnow())
        logger.debug("Feed 数据加载完成，共 %d 条信号", len(feed))
        return feed
    except Exception as exc:
        logger.error("Feed 数据加载失败，返回空列表: %s", exc, exc_info=True)
        return []
