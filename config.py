"""
sentinelflow/config.py
─────────────────────────────────────────────────────────
应用全局配置 — Single Source of Truth

所有颜色、URL、尺寸、文案均在此定义。
其他模块只做 `from config import APP_CONFIG`，绝不自己写死任何值。
─────────────────────────────────────────────────────────
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThemeColors:
    """
    Bloomberg 暗色终端调色板。

    frozen=True: 运行时不可修改，相当于编译期常量。
    需要换主题时只改这一个 dataclass，全站颜色跟着变。
    """
    bg_primary:   str = "#0a0e1a"   # 最深背景
    bg_secondary: str = "#0d1117"   # 卡片背景
    bg_tertiary:  str = "#161b22"   # 选中 Tab 背景

    border_default: str = "#21263a"
    border_muted:   str = "#30363d"

    accent_green:  str = "#21e786"  # 看涨 / 在线
    accent_red:    str = "#f85149"  # 看跌 / 高风险
    accent_blue:   str = "#58a6ff"  # 中性 / 信息
    accent_yellow: str = "#e3b341"  # 中等风险 / 警告

    text_primary: str = "#c9d1d9"
    text_muted:   str = "#8b949e"
    text_dim:     str = "#484f58"


@dataclass(frozen=True)
class LayoutConfig:
    """UI 尺寸配置（单位：像素）。"""
    chart_height:           int = 600
    chart_component_height: int = 620   # st.components.v1.html height 参数
    feed_scroll_height:     int = 480   # CSS height
    feed_component_height:  int = 500   # st.components.v1.html height 参数
    source_matrix_height:   int = 480


@dataclass(frozen=True)
class TradingViewConfig:
    """TradingView Advanced Chart Widget 配置。"""
    # CDN 脚本地址 — 抽出来方便日后替换为自托管版本
    script_url: str = (
        "https://s3.tradingview.com/external-embedding/"
        "embed-widget-advanced-chart.js"
    )
    default_symbol:   str = "AMEX:SPY"
    default_interval: str = "15"        # 分钟
    timezone:         str = "Asia/Tokyo"
    theme:            str = "dark"
    grid_color:       str = "#1a2030"

    # 默认叠加技术指标列表
    default_studies: list[str] = field(default_factory=lambda: [
        "RSI@tv-basicstudies",
        "MAExp@tv-basicstudies",
    ])


@dataclass(frozen=True)
class FeedConfig:
    """舆情 Feed 时间戳生成参数。"""
    # 相邻条目之间的基准时间间隔（秒）
    timestamp_base_interval: int = 47
    # 叠加随机抖动的最大值（秒），模拟真实采集延迟
    timestamp_jitter_max:    int = 30


@dataclass(frozen=True)
class AppConfig:
    """顶层配置，聚合所有子配置。整个应用只实例化一次。"""
    page_title:   str = "SentinelFlow | Sentiment OS"
    page_icon:    str = "📡"
    app_name:     str = "SENTINELFLOW"
    app_subtitle: str = "OMNI-CHANNEL SENTIMENT MONITORING SYSTEM"

    # Module A Ticker 下拉选项（格式：EXCHANGE:SYMBOL）
    available_tickers: list[str] = field(default_factory=lambda: [
        "AMEX:SPY",
        "BINANCE:BTCUSDT",
        "NASDAQ:QQQ",
        "NYSE:NVDA",
        "NASDAQ:TSLA",
        "SSE:000001",
        "NASDAQ:INTC",
    ])

    # Header 状态栏展示值
    sources_active:      int = 5
    sources_paused:      int = 2
    display_latency_avg: str = "~2.1s"

    # 子配置
    theme:       ThemeColors      = field(default_factory=ThemeColors)
    layout:      LayoutConfig     = field(default_factory=LayoutConfig)
    tradingview: TradingViewConfig = field(default_factory=TradingViewConfig)
    feed:        FeedConfig       = field(default_factory=FeedConfig)


# ──────────────────────────────────────────────
# 全局单例：其他模块统一 import 此对象
# ──────────────────────────────────────────────
APP_CONFIG = AppConfig()
