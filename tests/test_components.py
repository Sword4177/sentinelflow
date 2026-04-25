"""
tests/test_components.py
─────────────────────────────────────────────────────────
组件层单元测试

测试 feed_card.py 和 tradingview.py 中的纯 HTML 生成函数。
这类测试不依赖 Streamlit，执行速度极快。
─────────────────────────────────────────────────────────
"""
import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.feed_card import render_feed_card, _SENTIMENT_MAP
from components.tradingview import build_tradingview_widget
from data.feed import FeedEntry


# ──────────────────────────────────────────────
# components/feed_card.py
# ──────────────────────────────────────────────

def _make_entry(sentiment: str = "BULL") -> FeedEntry:
    """测试用 FeedEntry 工厂函数。"""
    return FeedEntry(
        source="TEST_SRC",
        tier="T1",
        sentiment=sentiment,
        text="Test signal text",
        time="12:34:56",
    )


class TestRenderFeedCard:
    """测试 render_feed_card() 输出的 HTML 正确性。"""

    def test_bull_uses_correct_css_class(self):
        """BULL 信号应使用默认 feed-card 类（绿色左边框）。"""
        html = render_feed_card(_make_entry("BULL"))
        assert 'class="feed-card"' in html
        assert "bearish" not in html
        assert "neutral" not in html

    def test_bear_uses_bearish_class(self):
        """BEAR 信号应使用 feed-card bearish 类。"""
        html = render_feed_card(_make_entry("BEAR"))
        assert "bearish" in html

    def test_neut_uses_neutral_class(self):
        """NEUT 信号应使用 feed-card neutral 类。"""
        html = render_feed_card(_make_entry("NEUT"))
        assert "neutral" in html

    def test_source_appears_in_output(self):
        """source 字段必须出现在输出 HTML 中。"""
        html = render_feed_card(_make_entry())
        assert "TEST_SRC" in html

    def test_time_appears_in_output(self):
        """time 字段必须出现在输出 HTML 中。"""
        html = render_feed_card(_make_entry())
        assert "12:34:56" in html

    def test_text_appears_in_output(self):
        """text 字段内容必须出现在输出 HTML 中。"""
        html = render_feed_card(_make_entry())
        assert "Test signal text" in html

    def test_bull_tag_contains_bullish_text(self):
        """BULL 信号的 badge 应包含 'BULLISH' 字样。"""
        html = render_feed_card(_make_entry("BULL"))
        assert "BULLISH" in html

    def test_bear_tag_contains_bearish_text(self):
        """BEAR 信号的 badge 应包含 'BEARISH' 字样。"""
        html = render_feed_card(_make_entry("BEAR"))
        assert "BEARISH" in html

    def test_unknown_sentiment_returns_nonempty_string(self):
        """
        未知情绪标签应降级为 NEUTRAL 渲染，不返回空字符串，
        不抛出异常（防止批量 join 时产生意外空洞）。
        """
        entry = _make_entry()
        entry["sentiment"] = "VERY_BULL_WOW"  # type: ignore[typeddict-item]
        html = render_feed_card(entry)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_missing_key_returns_empty_string(self):
        """
        FeedEntry 缺少必要键时，应返回空字符串（不崩溃），
        确保批量渲染时单条失败不影响整个 Feed。
        """
        broken_entry: dict = {"source": "X"}  # type: ignore[assignment]
        result = render_feed_card(broken_entry)  # type: ignore[arg-type]
        assert result == ""

    def test_all_sentiment_types_covered_in_map(self):
        """_SENTIMENT_MAP 必须覆盖三种合法情绪标签。"""
        for sentiment in ("BULL", "BEAR", "NEUT"):
            assert sentiment in _SENTIMENT_MAP


# ──────────────────────────────────────────────
# components/tradingview.py
# ──────────────────────────────────────────────

class TestBuildTradingviewWidget:
    """测试 build_tradingview_widget() 输出的 HTML 合法性。"""

    def test_output_is_string(self):
        """返回值必须是字符串。"""
        result = build_tradingview_widget()
        assert isinstance(result, str)

    def test_output_contains_script_tag(self):
        """输出必须包含 script 标签（Widget 核心）。"""
        result = build_tradingview_widget()
        assert "<script" in result

    def test_output_contains_symbol(self):
        """自定义 symbol 必须出现在输出中。"""
        result = build_tradingview_widget(symbol="NYSE:NVDA")
        assert "NYSE:NVDA" in result

    def test_default_symbol_used_when_none(self):
        """不传 symbol 时应使用配置中的 default_symbol。"""
        from config import APP_CONFIG
        result = build_tradingview_widget(symbol=None)
        assert APP_CONFIG.tradingview.default_symbol in result

    def test_height_appears_in_output(self):
        """自定义 height 必须反映在输出的内联样式中。"""
        result = build_tradingview_widget(height=999)
        assert "999px" in result

    def test_output_contains_valid_json_config(self):
        """
        Widget 配置部分必须是合法 JSON（核心安全性测试）。
        原版 f-string 手拼 JSON 无法保证这一点。
        """
        result = build_tradingview_widget(symbol="NASDAQ:TSLA")
        # 提取 script 标签内的 JSON 块
        script_start = result.find("<script")
        script_end   = result.find("</script>")
        assert script_start != -1 and script_end != -1

        script_block = result[script_start:script_end]
        # 找到第一个 { 到最后一个 } 之间的内容
        json_start = script_block.find("{")
        json_end   = script_block.rfind("}") + 1
        assert json_start != -1, "Widget 输出中未找到 JSON 配置块"

        json_str = script_block[json_start:json_end]
        try:
            config = json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"Widget 输出的 JSON 不合法: {e}\n内容: {json_str[:200]}")

        assert config["symbol"] == "NASDAQ:TSLA"
        assert config["theme"] == "dark"
        assert isinstance(config["studies"], list)

    def test_special_characters_in_symbol_dont_break_json(self):
        """
        symbol 中含特殊字符（如引号）时，json.dumps 应正确转义，
        不产生非法 JSON（原版 f-string 的核心 Bug）。
        """
        # 实际不会出现这种 ticker，但验证转义机制本身
        result = build_tradingview_widget(symbol='TEST"INJECT')
        script_start = result.find("<script")
        script_end   = result.find("</script>")
        script_block = result[script_start:script_end]
        json_start = script_block.find("{")
        json_end   = script_block.rfind("}") + 1
        json_str   = script_block[json_start:json_end]

        # 只要能解析，说明特殊字符被正确转义
        try:
            json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"特殊字符导致 JSON 非法: {e}")

    def test_error_returns_string_not_exception(self):
        """
        即使传入异常参数，函数也应返回字符串（降级 HTML），
        不应抛出异常传播到 UI 层。
        """
        # 传入极端 height 值
        result = build_tradingview_widget(height=-1)
        assert isinstance(result, str)
