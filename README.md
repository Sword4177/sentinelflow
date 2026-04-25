# 📡 SentinelFlow — Omni-Channel Sentiment Monitoring System

Bloomberg 暗色终端风格的金融舆情监控仪表盘，基于 Streamlit 构建。

---

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py
```

---

## 项目结构

```
sentinelflow/
├── app.py                   # 入口：页面配置 + CSS 注入 + Tab 路由
├── config.py                # 全局配置（Single Source of Truth）
├── styles.py                # CSS 生成器（从 ThemeColors 派生，零硬编码色值）
├── requirements.txt
│
├── data/                    # 数据层（纯数据，零 UI 依赖）
│   ├── feed.py              # 舆情信号 Feed（Mock → 可替换为真实 API）
│   ├── sources.py           # 数据源采集路线图 DataFrame
│   └── compliance.py        # 各渠道 ToS 合规风险评级
│
├── components/              # 可复用 UI 组件（HTML 渲染器）
│   ├── header.py            # 顶部状态栏
│   ├── feed_card.py         # 舆情信号卡片
│   └── tradingview.py       # TradingView Widget 注入器
│
├── pages/                   # 页面层（组合 data + components）
│   ├── module_a.py          # 实时行情 + 舆情 Feed
│   ├── module_b.py          # 数据源矩阵与实施路线图
│   └── module_c.py          # 合规风险雷达
│
└── tests/                   # 单元测试（52 个测试，无 Streamlit 依赖）
    ├── test_config.py
    ├── test_data.py
    └── test_components.py
```

---

## 架构原则

| 原则 | 实现方式 |
|------|---------|
| **单一职责** | `data/` 只取数，`components/` 只渲染，`pages/` 只组合，`app.py` 只路由 |
| **单一真相来源** | 所有常量集中于 `config.py`，其余文件 `from config import APP_CONFIG` |
| **不可变配置** | `@dataclass(frozen=True)` 防止运行时意外修改配置 |
| **开闭原则** | `feed_card.py` 用 `_SENTIMENT_MAP` 字典替代 `if-elif`，新增情绪类型无需改函数体 |
| **防御性编程** | 所有函数有 `try-except`，失败时返回安全降级值（空列表/空字符串/错误提示 HTML） |
| **可测试性** | 纯函数（无 Streamlit 副作用）单独提取，可直接 `pytest` |

---

## 运行测试

```bash
pytest tests/ -v
# 预期输出：52 passed
```

---

## 扩展指南

### 替换为真实数据源

修改 `data/feed.py` 的 `get_feed_data()` 函数内部，保持返回 `list[FeedEntry]` 不变：

```python
@st.cache_data(ttl=60)
def get_feed_data() -> list[FeedEntry]:
    # 替换这里的实现
    response = requests.get(APEWISDOM_API_URL, timeout=5)
    return [parse_entry(item) for item in response.json()["results"]]
```

### 新增情绪标签

在 `components/feed_card.py` 的 `_SENTIMENT_MAP` 中添加一行：

```python
_SENTIMENT_MAP: dict[str, tuple[str, str]] = {
    "BULL": (...),
    "BEAR": (...),
    "NEUT": (...),
    "VERY_BULL": ("feed-card", '<span class="feed-tag-bull">🚀 EXTREME BULL</span>'),  # 新增
}
```

### 修改主题颜色

只改 `config.py` 的 `ThemeColors`，全站颜色自动联动：

```python
@dataclass(frozen=True)
class ThemeColors:
    accent_green: str = "#00ff88"  # 改这一行
    ...
```
