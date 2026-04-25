"""
sentinelflow/components/feed_card.py
─────────────────────────────────────────────────────────
舆情信号卡片 HTML 渲染器

核心改进：用查表法（_SENTIMENT_MAP）替换 if-elif 链。
新增情绪类型时只需在 _SENTIMENT_MAP 中加一行，函数体零修改。
─────────────────────────────────────────────────────────
"""
import logging

from data.feed import FeedEntry

logger = logging.getLogger(__name__)

# 情绪标签 → (CSS class, HTML badge) 映射表
# 用 dict 替换 if-elif，符合「开闭原则」（对扩展开放，对修改关闭）
_SENTIMENT_MAP: dict[str, tuple[str, str]] = {
    "BULL": ("feed-card",         '<span class="feed-tag-bull">▲ BULLISH</span>'),
    "BEAR": ("feed-card bearish", '<span class="feed-tag-bear">▼ BEARISH</span>'),
    "NEUT": ("feed-card neutral", '<span class="feed-tag-neu">◆ NEUTRAL</span>'),
}
_FALLBACK: tuple[str, str] = (
    "feed-card neutral",
    '<span class="feed-tag-neu">◆ UNKNOWN</span>',
)


def render_feed_card(entry: FeedEntry) -> str:
    """
    将单条 FeedEntry 渲染为 HTML 字符串（feed-card 样式）。

    Args:
        entry: 包含 source / sentiment / time / text 字段的舆情条目。

    Returns:
        可拼接至 ``st.components.v1.html()`` 的 HTML 片段字符串。
        若渲染出错（缺字段 / 未知情绪），返回空字符串，
        确保批量渲染时单条失败不影响整体 Feed 展示。
    """
    try:
        sentiment = entry["sentiment"]
        css_class, tag_html = _SENTIMENT_MAP.get(sentiment, _FALLBACK)

        if sentiment not in _SENTIMENT_MAP:
            logger.warning("未知情绪标签 '%s'，使用 NEUTRAL 降级渲染", sentiment)

        return (
            f'<div class="{css_class}">'
            f'  <span class="feed-source">{entry["source"]}</span>'
            f'  <span class="feed-time">{entry["time"]}</span>'
            f'  <div class="feed-text">{tag_html} &nbsp; {entry["text"]}</div>'
            f"</div>\n"
        )
    except KeyError as exc:
        logger.error("FeedEntry 缺少必要字段 %s，跳过此卡片", exc)
        return ""
    except Exception as exc:
        logger.error("Feed 卡片渲染失败: %s", exc, exc_info=True)
        return ""
