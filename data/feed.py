"""
sentinelflow/data/feed.py
─────────────────────────────────────────────────────────
舆情 Feed 数据层 — 多数据源聚合器

数据源优先级（按 Tier 分层）：
  T1-A: ApeWisdom REST API  — Reddit 股票提及排行（免费，无 token）
  T1-B: Reddit Public JSON  — WSB/stocks/investing 热帖（免费，无 token）
  降级: Mock 数据            — 所有 T1 源不可达时自动切换

架构原则：
  - 每个数据源有独立的 fetch + parse 函数，互不耦合
  - _aggregate() 负责合并多源数据，上层只调用 get_feed_data()
  - get_feed_data() 签名和返回类型永远不变
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
# 全局配置常量
# ──────────────────────────────────────────────
_REQUEST_TIMEOUT = 8  # 秒，超时即降级

# ApeWisdom
_APEWISDOM_URL         = "https://apewisdom.io/api/v1.0/filter/all-stocks/page/1"
_APEWISDOM_MAX_RESULTS = 10

# Reddit 公开 JSON API（无需 token）
_REDDIT_SUBREDDITS = ["wallstreetbets", "stocks", "investing"]
_REDDIT_MAX_POSTS  = 5   # 每个版块取前 N 条
_REDDIT_HEADERS    = {"User-Agent": "sentinelflow/1.0 (financial sentiment monitor)"}

# 情绪判断阈值（ApeWisdom 排名变化）
_RANK_BULL_THRESHOLD = 5
_RANK_BEAR_THRESHOLD = -5

# Reddit 情绪阈值（upvote_ratio）
_REDDIT_BULL_RATIO = 0.85
_REDDIT_BEAR_RATIO = 0.60


# ──────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────
class FeedEntry(TypedDict):
    """
    单条舆情信号的数据结构。

    使用 TypedDict 使 IDE 可对键名做静态检查，
    比 dataclass 更轻量（无需实例化开销）。
    """
    source:    str   # 数据源，如 "APEWISDOM" / "REDDIT/WSB"
    tier:      str   # 分层标识，如 "T1"
    sentiment: str   # "BULL" | "BEAR" | "NEUT"
    text:      str   # 信号文本
    time:      str   # HH:MM:SS UTC 格式时间戳


# ──────────────────────────────────────────────
# 情绪判断工具函数（纯函数，无副作用，便于测试）
# ──────────────────────────────────────────────
def _parse_sentiment_by_rank(rank_now: int, rank_24h: int) -> str:
    """
    根据 ApeWisdom 排名变化判断情绪。

    排名数字越小越靠前（rank=1 最热）。
    rank_now < rank_24h 表示排名上升，为 BULL。

    Args:
        rank_now: 当前排名
        rank_24h: 24小时前排名

    Returns:
        "BULL" | "BEAR" | "NEUT"
    """
    delta = rank_24h - rank_now
    if delta >= _RANK_BULL_THRESHOLD:
        return "BULL"
    elif delta <= _RANK_BEAR_THRESHOLD:
        return "BEAR"
    return "NEUT"


def _parse_sentiment_by_ratio(upvote_ratio: float) -> str:
    """
    根据 Reddit 帖子 upvote_ratio 判断情绪。

    Args:
        upvote_ratio: Reddit 返回的点赞比例，0.0~1.0

    Returns:
        "BULL" | "BEAR" | "NEUT"
    """
    if upvote_ratio >= _REDDIT_BULL_RATIO:
        return "BULL"
    elif upvote_ratio <= _REDDIT_BEAR_RATIO:
        return "BEAR"
    return "NEUT"


# ──────────────────────────────────────────────
# ApeWisdom 数据源
# ──────────────────────────────────────────────
def _parse_apewisdom_item(item: dict, now: datetime) -> FeedEntry:
    """将 ApeWisdom 单条 API 响应转换为 FeedEntry。"""
    ticker       = item.get("ticker", "???")
    name         = item.get("name", ticker)
    mentions     = item.get("mentions", 0)
    upvotes      = item.get("upvotes", 0)
    rank_now     = item.get("rank", 99)
    rank_24h     = item.get("rank_24h_ago", 99)
    mentions_24h = item.get("mentions_24h_ago", 0)

    sentiment  = _parse_sentiment_by_rank(rank_now, rank_24h)
    rank_delta = rank_24h - rank_now
    arrow      = f"↑{rank_delta}" if rank_delta > 0 else (f"↓{abs(rank_delta)}" if rank_delta < 0 else "→")
    mention_delta = mentions - mentions_24h
    mention_str   = f"+{mention_delta}" if mention_delta >= 0 else str(mention_delta)

    return FeedEntry(
        source="APEWISDOM", tier="T1", sentiment=sentiment,
        time=now.strftime("%H:%M:%S"),
        text=(
            f"${ticker} ({name}) — rank #{rank_now} {arrow} | "
            f"mentions {mentions} ({mention_str} vs 24h) | upvotes {upvotes}"
        ),
    )


def _fetch_apewisdom(now: datetime) -> list[FeedEntry]:
    """
    从 ApeWisdom API 拉取实时股票提及数据。

    降级策略：超时 / HTTP 错误 / 解析失败 → 返回空列表，由聚合器降级。
    """
    try:
        resp = requests.get(_APEWISDOM_URL, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])[:_APEWISDOM_MAX_RESULTS]
        entries = [_parse_apewisdom_item(item, now) for item in results]
        logger.info("ApeWisdom: 拉取 %d 条", len(entries))
        return entries
    except requests.Timeout:
        logger.warning("ApeWisdom 超时，跳过")
        return []
    except Exception as exc:
        logger.warning("ApeWisdom 异常: %s，跳过", exc)
        return []


# ──────────────────────────────────────────────
# Reddit 公开 JSON API 数据源
# ──────────────────────────────────────────────
def _parse_reddit_post(post: dict, subreddit: str, now: datetime) -> FeedEntry | None:
    """
    将 Reddit 单条帖子转换为 FeedEntry。

    Args:
        post:      Reddit API 返回的单条 post data dict
        subreddit: 来源版块名称
        now:       当前 UTC 时间

    Returns:
        FeedEntry 或 None（帖子数据不完整时跳过）
    """
    try:
        data         = post.get("data", {})
        title        = data.get("title", "")
        score        = data.get("score", 0)
        num_comments = data.get("num_comments", 0)
        upvote_ratio = data.get("upvote_ratio", 0.5)
        author       = data.get("author", "unknown")

        if not title:
            return None

        sentiment = _parse_sentiment_by_ratio(upvote_ratio)
        source    = f"REDDIT/{subreddit.upper()[:3]}"

        return FeedEntry(
            source=source, tier="T1", sentiment=sentiment,
            time=now.strftime("%H:%M:%S"),
            text=(
                f"[r/{subreddit}] {title[:80]}{'...' if len(title) > 80 else ''} "
                f"| ▲{score} | 💬{num_comments} | by u/{author}"
            ),
        )
    except Exception as exc:
        logger.warning("Reddit 帖子解析失败: %s", exc)
        return None


def _fetch_reddit_subreddit(subreddit: str, now: datetime) -> list[FeedEntry]:
    """
    从单个 subreddit 的公开 JSON API 拉取热帖。

    使用 Reddit 公开 JSON 接口，无需注册应用或 token。
    User-Agent 必须设置，否则 Reddit 返回 429。

    降级策略：任何失败 → 返回空列表。
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={_REDDIT_MAX_POSTS}"
    try:
        resp = requests.get(url, headers=_REDDIT_HEADERS, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        posts = resp.json().get("data", {}).get("children", [])
        entries = [
            entry for post in posts
            if (entry := _parse_reddit_post(post, subreddit, now)) is not None
        ]
        logger.info("Reddit r/%s: 拉取 %d 条", subreddit, len(entries))
        return entries
    except requests.Timeout:
        logger.warning("Reddit r/%s 超时，跳过", subreddit)
        return []
    except Exception as exc:
        logger.warning("Reddit r/%s 异常: %s，跳过", subreddit, exc)
        return []


def _fetch_reddit(now: datetime) -> list[FeedEntry]:
    """聚合所有配置的 subreddit 数据。"""
    entries: list[FeedEntry] = []
    for subreddit in _REDDIT_SUBREDDITS:
        entries.extend(_fetch_reddit_subreddit(subreddit, now))
    return entries


# ──────────────────────────────────────────────
# 降级 Mock 数据
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
    """降级 Mock 数据构建器。"""
    entries: list[FeedEntry] = []
    for i, (source, tier, sentiment, text) in enumerate(_MOCK_ENTRIES):
        jitter = random.randint(0, cfg.timestamp_jitter_max)
        offset = i * cfg.timestamp_base_interval + jitter
        ts     = base_time - timedelta(seconds=offset)
        entries.append(FeedEntry(
            source=source, tier=tier,
            sentiment=sentiment, text=text,
            time=ts.strftime("%H:%M:%S"),
        ))
    return entries


# ──────────────────────────────────────────────
# 多数据源聚合器
# ──────────────────────────────────────────────
def _aggregate(now: datetime) -> list[FeedEntry]:
    """
    并发调用所有 T1 数据源并合并结果。

    合并规则：ApeWisdom 在前（排名信号更直接），Reddit 在后（原文内容更丰富）。
    任何单个数据源失败不影响其他源。

    Returns:
        合并后的 FeedEntry 列表，失败时返回空列表。
    """
    entries: list[FeedEntry] = []
    entries.extend(_fetch_apewisdom(now))
    entries.extend(_fetch_reddit(now))
    return entries


# ──────────────────────────────────────────────
# 公开接口（唯一对外暴露的函数）
# ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_feed_data() -> list[FeedEntry]:
    """
    获取多渠道舆情信号列表。

    数据来源优先级：
      1. T1 聚合（ApeWisdom + Reddit）
      2. Mock 数据（所有 T1 源失败时自动降级）

    TTL=60s：避免频繁请求的同时保证数据相对新鲜。

    Returns:
        FeedEntry 列表，最新信号在前。
    """
    try:
        now     = datetime.utcnow()
        entries = _aggregate(now)

        if entries:
            logger.info("Feed 聚合完成：共 %d 条信号", len(entries))
            return entries

        logger.warning("所有 T1 数据源返回空，降级至 Mock 数据")
        return _build_mock_entries(APP_CONFIG.feed, now)

    except Exception as exc:
        logger.error("Feed 数据加载完全失败: %s", exc, exc_info=True)
        return []
