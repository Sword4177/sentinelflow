"""
sentinelflow/styles.py
─────────────────────────────────────────────────────────
全局 CSS 生成器

核心原则：CSS 中零硬编码色值。
所有颜色通过 f-string 从 ThemeColors 注入，
换肤只需修改 config.py。
─────────────────────────────────────────────────────────
"""
import logging

from config import APP_CONFIG, ThemeColors

logger = logging.getLogger(__name__)


def build_global_css(colors: ThemeColors | None = None) -> str:
    """
    根据主题色板构建完整的全局 CSS 字符串。

    Args:
        colors: 主题色板实例。为 None 时使用 APP_CONFIG.theme。

    Returns:
        可直接传入 ``st.markdown(..., unsafe_allow_html=True)`` 的 CSS 字符串。
        构建失败时返回空字符串（降级：使用 Streamlit 默认样式），并记录 ERROR 日志。
    """
    if colors is None:
        colors = APP_CONFIG.theme

    try:
        return f"""
<style>
    /* ── 隐藏 Streamlit 默认顶部工具栏（防止遮挡 Header）── */
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; }}

    /* ── 基础背景 ── */
    .stApp {{ background-color: {colors.bg_primary}; color: {colors.text_primary}; }}
    .block-container {{ padding: 1rem 2rem 2rem 2rem; }}

    /* ── Header ── */
    .sentinel-header {{
        background: linear-gradient(90deg, {colors.bg_secondary} 0%, {colors.bg_tertiary} 100%);
        border-bottom: 1px solid {colors.accent_green};
        padding: 12px 0 8px 0;
        margin-bottom: 1.5rem;
    }}
    .sentinel-title {{
        font-family: 'Courier New', monospace;
        font-size: 1.6rem; font-weight: 700;
        color: {colors.accent_green};
        letter-spacing: 3px; margin: 0;
    }}
    .sentinel-sub {{
        font-family: 'Courier New', monospace;
        font-size: 0.72rem; color: {colors.accent_blue};
        letter-spacing: 2px; margin-top: 2px;
    }}

    /* ── Tab 导航 ── */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {colors.bg_secondary};
        border-bottom: 1px solid {colors.border_muted}; gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Courier New', monospace; font-size: 0.78rem;
        color: {colors.text_muted}; letter-spacing: 1px;
        padding: 8px 20px; border-radius: 4px 4px 0 0;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {colors.bg_tertiary} !important;
        color: {colors.accent_green} !important;
        border-bottom: 2px solid {colors.accent_green} !important;
    }}

    /* ── 舆情信号卡片 ── */
    .feed-card {{
        background: {colors.bg_secondary};
        border: 1px solid {colors.border_default};
        border-left: 3px solid {colors.accent_green};
        border-radius: 4px; padding: 8px 12px; margin-bottom: 6px;
        font-family: 'Courier New', monospace; font-size: 0.72rem;
    }}
    .feed-card.bearish {{ border-left-color: {colors.accent_red}; }}
    .feed-card.neutral {{ border-left-color: {colors.accent_blue}; }}

    .feed-source {{ color: {colors.accent_blue}; font-size: 0.65rem; letter-spacing: 1px; }}
    .feed-time   {{ color: {colors.text_dim}; font-size: 0.62rem; float: right; }}
    .feed-text   {{ color: {colors.text_primary}; margin-top: 3px; line-height: 1.4; }}
    .feed-tag-bull {{ color: {colors.accent_green}; font-weight: 700; }}
    .feed-tag-bear {{ color: {colors.accent_red}; font-weight: 700; }}
    .feed-tag-neu  {{ color: {colors.accent_blue}; font-weight: 700; }}

    /* ── Metric 卡片 ── */
    div[data-testid="stMetric"] {{
        background: {colors.bg_secondary};
        border: 1px solid {colors.border_default};
        border-radius: 6px; padding: 12px 16px;
    }}
    div[data-testid="stMetricLabel"] {{ color: {colors.text_muted}; font-size: 0.72rem; }}
    div[data-testid="stMetricValue"] {{ color: {colors.text_primary}; font-size: 1.4rem; }}

    /* ── 风险卡片（三级）── */
    .risk-high {{
        background: #2d0d0d;
        border: 1px solid {colors.accent_red};
        border-left: 4px solid {colors.accent_red};
        border-radius: 4px; padding: 12px 16px; margin-bottom: 10px;
        font-family: 'Courier New', monospace; font-size: 0.75rem;
    }}
    .risk-mod {{
        background: #1f1a08;
        border: 1px solid {colors.accent_yellow};
        border-left: 4px solid {colors.accent_yellow};
        border-radius: 4px; padding: 12px 16px; margin-bottom: 10px;
        font-family: 'Courier New', monospace; font-size: 0.75rem;
    }}
    .risk-low {{
        background: #0d1f17;
        border: 1px solid {colors.accent_green};
        border-left: 4px solid {colors.accent_green};
        border-radius: 4px; padding: 12px 16px; margin-bottom: 10px;
        font-family: 'Courier New', monospace; font-size: 0.75rem;
    }}
    .risk-label  {{ font-size: 0.65rem; letter-spacing: 1px; margin-bottom: 4px; }}
    .risk-source {{ font-weight: 700; font-size: 0.85rem; margin-bottom: 6px; }}
    .risk-note   {{ color: {colors.text_muted}; line-height: 1.5; }}

    /* ── 通用辅助 ── */
    .stDataFrame {{ background: {colors.bg_secondary}; }}
    iframe {{ border: none !important; }}
    .section-label {{
        font-family: 'Courier New', monospace; font-size: 0.65rem;
        color: {colors.text_dim}; letter-spacing: 2px; text-transform: uppercase;
        border-bottom: 1px solid {colors.border_default};
        padding-bottom: 4px; margin-bottom: 10px;
    }}
    .dot-green {{ color: {colors.accent_green}; }}
    .dot-red   {{ color: {colors.accent_red}; }}
    .status-bar {{
        font-family: 'Courier New', monospace; font-size: 0.65rem;
        color: {colors.text_dim}; letter-spacing: 1px; margin-top: 4px;
    }}
</style>
"""
    except Exception as exc:
        # 降级策略：CSS 构建失败不应中断应用主流程，记录错误，返回空字符串
        logger.error("CSS 样式构建失败，回退至 Streamlit 默认样式: %s", exc, exc_info=True)
        return ""
