"""
tests/test_config.py
─────────────────────────────────────────────────────────
配置层测试

测试目标：
  - APP_CONFIG 可正常实例化
  - frozen=True 防止意外修改
  - 所有颜色值格式合法（# + 6位十六进制）
─────────────────────────────────────────────────────────
"""
import re
import pytest
from dataclasses import FrozenInstanceError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import APP_CONFIG, ThemeColors, AppConfig


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TestAppConfig:
    """顶层配置对象的基本健全性检查。"""

    def test_singleton_instantiation(self):
        """APP_CONFIG 应为合法的 AppConfig 实例。"""
        assert isinstance(APP_CONFIG, AppConfig)

    def test_page_title_not_empty(self):
        """页面标题不应为空字符串。"""
        assert APP_CONFIG.page_title.strip() != ""

    def test_available_tickers_not_empty(self):
        """Ticker 列表至少有一个条目。"""
        assert len(APP_CONFIG.available_tickers) > 0

    def test_ticker_format(self):
        """每个 Ticker 必须符合 EXCHANGE:SYMBOL 格式。"""
        for ticker in APP_CONFIG.available_tickers:
            assert ":" in ticker, f"Ticker 格式错误: {ticker}"

    def test_sources_active_positive(self):
        """活跃数据源数量必须为正整数。"""
        assert APP_CONFIG.sources_active > 0

    def test_frozen_immutability(self):
        """frozen=True：运行时修改配置应抛出 FrozenInstanceError。"""
        with pytest.raises(FrozenInstanceError):
            APP_CONFIG.page_title = "HACKED"  # type: ignore[misc]


class TestThemeColors:
    """主题色板的格式与不可变性检查。"""

    def test_all_colors_are_valid_hex(self):
        """
        ThemeColors 中所有颜色字段必须是合法的 6 位十六进制颜色值。
        这个测试会在有人写错颜色（如 '#gggggg'）时立即报警。
        """
        colors = APP_CONFIG.theme
        color_fields = {
            k: v for k, v in vars(colors).items()
            if isinstance(v, str) and v.startswith("#")
        }
        assert len(color_fields) > 0, "没有找到任何颜色字段"

        for field_name, color_value in color_fields.items():
            assert HEX_COLOR_RE.match(color_value), (
                f"ThemeColors.{field_name} = '{color_value}' 不是合法的 #RRGGBB 格式"
            )

    def test_theme_colors_immutable(self):
        """ThemeColors 同样是 frozen dataclass，不可修改。"""
        with pytest.raises(FrozenInstanceError):
            APP_CONFIG.theme.accent_green = "#ffffff"  # type: ignore[misc]


class TestTradingViewConfig:
    """TradingView 配置合理性检查。"""

    def test_script_url_is_https(self):
        """Widget 脚本必须通过 HTTPS 加载（CSP 合规）。"""
        url = APP_CONFIG.tradingview.script_url
        assert url.startswith("https://"), f"脚本 URL 不是 HTTPS: {url}"

    def test_default_studies_is_list(self):
        """default_studies 必须是列表，不能是其他可迭代类型。"""
        assert isinstance(APP_CONFIG.tradingview.default_studies, list)

    def test_chart_height_positive(self):
        """图表高度必须为正整数。"""
        assert APP_CONFIG.layout.chart_height > 0

    def test_component_height_gte_chart_height(self):
        """
        st.components.v1.html 的 height 参数必须 >= CSS height，
        否则图表会被截断。
        """
        layout = APP_CONFIG.layout
        assert layout.chart_component_height >= layout.chart_height
        assert layout.feed_component_height >= layout.feed_scroll_height
