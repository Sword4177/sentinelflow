"""
sentinelflow/data/feed.py
─────────────────────────────────────────────────────────
舆情 Feed 数据层 — ApeWisdom 真实 API 接入

数据源优先级：
  1. ApeWisdom REST API（免费，无需 token，实时 Reddit 股票提及数据）
  2. 降级 Mock 数据（API 不可达时自动切换，保证页面不崩溃）

接口设计与真实 API 同构：
  get_feed_data() 的签名和返回类型永远不变，
  上层 pages/module_a.py 完全不感知数据来源切换。
─────────────────────────────────────────────────────────
"""
import logging
import random
from datetime import datetime, timedelta
from typing import TypedDict

import requests
import streamlit as st

from config import APP_CONFIG, FeedConfig

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# ApeWisdom API 配置
# ──────────────────────────────────────────────
_APEWISDOM_URL = "https://apewisdom.io/api/v1.0/filter/all-stocks/page/1"
_REQUEST_TIMEOUT = 8  # 秒，超时即降级

# 情绪判断阈值：排名上升超过此值视为 BULL，下降超过此值视为 BEAR
_RANK_BULL_THRESHOLD = 5
_RANK_BEAR_THRESHOLD = -5


class FeedEntry(TypedDict):
    """
    单条舆情信号的数据结构。

    使用 TypedDict 而非 dict，使得 IDE 可以对键名做静态检查，
    同时比 dataclass 更轻量（无需实例化开销）。
    """
    source:    str   # 数据源名称，如 "APEWISDOM"
    tier:      str   # 分层标识，如 "T1"
    sentiment: str   # "BULL" | "BEAR" | "NEUT"
    text:      str   # 信号文本
    time:      str   # HH:MM:SS UTC 格式时间戳


def _parse_sentiment(rank_now: int, rank_24h: int) -> str:
    """
    根据排名变化判断情绪方向。

    排名数字越小越靠前（rank=1 最热）。
    rank_now < rank_24h 表示排名上升（更热），为 BULL。
    rank_now > rank_24h 表示排名下降（降温），为 BEAR。

    Args:
        rank_now: 当前排名
        rank_24h: 24小时前排名

    Returns:
        "BULL" | "BEAR" | "NEUT"
    """
    delta = rank_24h - rank_now  # 正数 = 排名上升
    if delta >= _RANK_BULL_THRESHOLD:
        return "BULL"
    elif delta <= _RANK_BEAR_THRESHOLD:
        return "BEAR"
    return "NEUT"


def _parse_apewisdom_item(item: dict, now: datetime) -> FeedEntry:
    """
    将 ApeWisdom 单条 API 响应转换为 FeedEntry。

    Args:
        item: ApeWisdom API 返回的单条记录 dict
        now:  当前 UTC 时间，用于生成时间戳

    Returns:
        FeedEntry 实例
    """
    ticker       = item.get("ticker", "???")
    name         = item.get("name", ticker)
    mentions     = item.get("mentions", 0)
    upvotes      = item.get("upvotes", 0)
    rank_now     = item.get("rank", 99)
    rank_24h     = item.get("rank_24h_ago", 99)
    mentions_24h = item.get("mentions_24h_ago", 0)

    sentiment = _parse_sentiment(rank_now, rank_24h)

    # 排名变化方向箭头
    rank_delta = rank_24h - rank_now
    if rank_delta > 0:
        arrow = f"↑{rank_delta}"
    elif rank_delta < 0:
        arrow = f"↓{abs(rank_delta)}"
    else:
        arrow = "→"

    # 提及量变化
    mention_delta = mentions - mentions_24h
    mention_str = f"+{mention_delta}" if mention_delta >= 0 else str(mention_delta)

    text = (
        f"${ticker} ({name}) — rank #{rank_now} {arrow} | "
        f"mentions {mentions} ({mention_str} vs 24h) | "
        f"upvotes {upvotes}"
    )

    return FeedEntry(
        source="APEWISDOM",
        tier="T1",
        sentiment=sentiment,
        text=text,
        time=now.strftime("%H:%M:%S"),
    )


def _fetch_apewisdom() -> list[FeedEntry]:
    """
    从 ApeWisdom API 拉取实时股票提及数据。

    降级策略：
        网络超时、HTTP 错误、JSON 解析失败时，
        记录 WARNING 并返回空列表，由调用方切换至 Mock 数据。

    Returns:
        FeedEntry 列表（最多 15 条），失败时返回空列表。
    """
    try:
        resp = requests.get(_APEWISDOM_URL, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])[:15]  # 只取前 15 条
        now = datetime.utcnow()
        entries = [_parse_apewisdom_item(item, now) for item in results]
        logger.info("ApeWisdom API 拉取成功，共 %d 条", len(entries))
        return entries
    except requests.Timeout:
        logger.warning("ApeWisdom API 超时（%ss），切换至 Mock 数据", _REQUEST_TIMEOUT)
        return []
    except requests.HTTPError as exc:
        logger.warning("ApeWisdom API HTTP 错误 %s，切换至 Mock 数据", exc)
        return []
    except Exception as exc:
        logger.warning("ApeWisdom API 异常: %s，切换至 Mock 数据", exc)
        return []


# ──────────────────────────────────────────────
# 降级 Mock 数据 — API 不可达时使用
# ──────────────────────────────────────────────
_MOCK_ENTRIES: list[tuple[str, str, str, str]] = [
    ("APEWISDOM",  "T1", "BULL", "$NVDA mentions +340% in 1hr — WSB momentum spike"),
    ("REDDIT/WSB", "T1", "BULL", "YOLO earnings play $TSLA — 847 upvotes 2min"),
    ("STOCKTWITS", "T1", "BEAR", "$SPY puts loading. Fed minutes dropped bearish."),
    ("GUBA/东财",  "T1", "BULL", "贵州茅台主力资金净流入 ¥12.3亿 异常放量"),
    ("APEWISDOM",  "T1", "BULL", "$AMD rank ↑ 47 positions — unusual mention surge"),
    ("REDDIT/INV", "T1", "BEAR", "Rate cut expectations collapsing — 10Y at 4.82%"),
    ("STOCKTWITS", "T1", "BULL", "$BTC breaking 98k — whale accumulation confirmed"),
    ("GUBA/东财",  "T1", "BEAR", "中概股集体跳水，纳指期货承压，情绪极度悲观"),
    ("TELEGRAM",   "T1", "NEUT", "智堡: 日央行政策会议纪要显示鸽派偏向未变"),
    ("REDDIT/STK", "T1", "BULL", "$INTC reversal pattern — support held at $21.4"),
]


def _build_mock_entries(cfg: FeedConfig, base_time: datetime) -> list[FeedEntry]:
    """降级 Mock 数据构建器，逻辑与原版保持一致。"""
    entries: list[FeedEntry] = []
    for i, (source, tier, sentiment, text) in enumerate(_MOCK_ENTRIES):
        jitter = random.randint(0, cfg.timestamp_jitter_max)
        offset = i * cfg.timestamp_base_interval + jitter
        ts = base_time - timedelta(seconds=offset)
        entries.append(FeedEntry(
            source=source, tier=tier,
            sentiment=sentiment, text=text,
            time=ts.strftime("%H:%M:%S"),
        ))
    return entries


@st.cache_data(ttl=60)
def get_feed_data() -> list[FeedEntry]:
    """
    获取多渠道舆情信号列表。

    数据来源优先级：
      1. ApeWisdom 真实 API（TTL=60s 缓存）
      2. Mock 数据（API 失败时自动降级）

    Returns:
        FeedEntry 列表，最新信号在前。
    """
    try:
        # 优先尝试真实 API
        entries = _fetch_apewisdom()
        if entries:
            return entries

        # API 返回空或失败，降级至 Mock
        logger.warning("ApeWisdom 返回空数据，使用 Mock 数据降级")
        return _build_mock_entries(APP_CONFIG.feed, datetime.utcnow())

    except Exception as exc:
        logger.error("Feed 数据加载完全失败: %s", exc, exc_info=True)
        return []
