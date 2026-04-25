"""
sentinelflow/components/tradingview.py
─────────────────────────────────────────────────────────
TradingView Advanced Chart Widget HTML 注入器

关键重构：原版用 f-string 手拼 JSON，存在两个风险：
  1. symbol 含特殊字符（如引号）会导致 Widget JS 解析崩溃；
  2. 配置字段散落在字符串里，极难维护。

重构后：用 json.dumps() 序列化配置 dict，彻底消除手拼 JSON。
─────────────────────────────────────────────────────────
"""
import json
import logging

from config import APP_CONFIG, TradingViewConfig

logger = logging.getLogger(__name__)


def build_tradingview_widget(
    symbol: str | None = None,
    height: int | None = None,
    cfg: TradingViewConfig | None = None,
) -> str:
    """
    生成 TradingView Advanced Chart 的完整 HTML 嵌入代码。

    Args:
        symbol: 交易所:代码格式标的，如 ``"NASDAQ:NVDA"``。
                为 None 时使用 ``cfg.default_symbol``。
        height: 图表高度（像素）。为 None 时使用 ``APP_CONFIG.layout.chart_height``。
        cfg:    TradingView 配置实例。为 None 时使用 ``APP_CONFIG.tradingview``。

    Returns:
        可传入 ``st.components.v1.html()`` 的 HTML 字符串。
        配置异常时返回包含错误提示的降级 HTML，页面不白屏。
    """
    if cfg is None:
        cfg = APP_CONFIG.tradingview
    if symbol is None:
        symbol = cfg.default_symbol
    if height is None:
        height = APP_CONFIG.layout.chart_height

    try:
        # 用 dict + json.dumps 替代手拼 JSON 字符串
        # ensure_ascii=False：保留中文字符，避免 \uXXXX 转义
        widget_config: dict = {
            "autosize":           True,
            "symbol":             symbol,
            "interval":           cfg.default_interval,
            "timezone":           cfg.timezone,
            "theme":              cfg.theme,
            "style":              "1",
            "locale":             "en",
            "backgroundColor":    APP_CONFIG.theme.bg_primary,
            "gridColor":          cfg.grid_color,
            "hide_top_toolbar":   False,
            "hide_legend":        False,
            "allow_symbol_change":True,
            "save_image":         False,
            "calendar":           False,
            "hide_volume":        False,
            "support_host":       "https://www.tradingview.com",
            "studies":            list(cfg.default_studies),
        }
        config_json = json.dumps(widget_config, ensure_ascii=False, indent=2)

        return (
            f'<div id="tv_chart_container"'
            f' style="height:{height}px; background:{APP_CONFIG.theme.bg_primary};">'
            f'  <div class="tradingview-widget-container" style="height:100%;">'
            f'    <div class="tradingview-widget-container__widget" style="height:100%;"></div>'
            f'    <script type="text/javascript"'
            f'      src="{cfg.script_url}" async>'
            f"    {config_json}"
            f"    </script>"
            f"  </div>"
            f"</div>"
        )

    except Exception as exc:
        logger.error(
            "TradingView Widget 构建失败 (symbol=%s, height=%s): %s",
            symbol, height, exc, exc_info=True,
        )
        # 降级：返回内联错误提示，不抛出异常
        return (
            f'<div style="color:{APP_CONFIG.theme.accent_red};'
            f' font-family:monospace; padding:16px;">'
            f"⚠ Chart load failed — {exc}"
            f"</div>"
        )
