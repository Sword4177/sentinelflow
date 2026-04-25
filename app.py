"""
sentinelflow/app.py
─────────────────────────────────────────────────────────
SentinelFlow — 多渠道金融舆情监控系统
入口文件

职责（且仅此三项）：
  1. 配置 Streamlit 页面
  2. 注入全局 CSS
  3. Tab 路由 → 各 Module 渲染函数

运行方式:
    streamlit run app.py
─────────────────────────────────────────────────────────
"""
import logging
import sys

import streamlit as st

from components.header import render_header
from config import APP_CONFIG
from pages.module_a import render_module_a
from pages.module_b import render_module_b
from pages.module_c import render_module_c
from pages.module_d import render_module_d
from styles import build_global_css

# ──────────────────────────────────────────────
# 日志配置
# 统一格式：时间 | 级别 | 模块名 | 消息
# 生产环境可将 stream 替换为 FileHandler 或接入 ELK
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 页面配置 — 必须是整个脚本的第一个 Streamlit 调用
# ──────────────────────────────────────────────
st.set_page_config(
    page_title=APP_CONFIG.page_title,
    page_icon=APP_CONFIG.page_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 全局 CSS 注入
# ──────────────────────────────────────────────
st.markdown(build_global_css(), unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
render_header()

# ──────────────────────────────────────────────
# Tab 路由 — app.py 不含任何业务逻辑
# ──────────────────────────────────────────────
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "  📈  MODULE A — LIVE MARKET & SENTIMENT  ",
    "  🗂️  MODULE B — DATA SOURCE MATRIX  ",
    "  ⚖️  MODULE C — COMPLIANCE RADAR  ",
    "  📡  MODULE D — TRUTH SIGNAL  ",
])

with tab_a:
    render_module_a()

with tab_b:
    render_module_b()

with tab_c:
    render_module_c()

with tab_d:
    render_module_d()

logger.debug("页面渲染完成")
