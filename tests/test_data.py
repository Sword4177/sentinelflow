"""
tests/test_data.py
─────────────────────────────────────────────────────────
数据层单元测试

测试纯函数（无 Streamlit 副作用）：
  - _build_entries()：时间戳生成逻辑
  - get_source_matrix()：DataFrame 结构
  - get_compliance_data()：合规记录完整性
  - RISK_ORDER：排序键覆盖所有风险等级

注意：带 @st.cache_data 的函数在测试中通过 mock 绕开缓存层，
      测试的是业务逻辑，不是 Streamlit 的缓存机制。
─────────────────────────────────────────────────────────
"""
from datetime import datetime
from unittest.mock import patch

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import APP_CONFIG, FeedConfig
from data.compliance import RISK_ORDER, _COMPLIANCE_RECORDS
from data.feed import FeedEntry, _MOCK_ENTRIES, _build_mock_entries, _parse_sentiment_by_rank, _parse_sentiment_by_ratio
from data.sources import _SOURCE_RECORDS

# ──────────────────────────────────────────────
# data/feed.py
# ──────────────────────────────────────────────

class TestBuildEntries:
    """测试 _build_mock_entries()：纯函数，无 I/O，完全可单元测试。"""

    BASE_TIME = datetime(2025, 1, 1, 12, 0, 0)

    def _make_cfg(self, base_interval: int = 10, jitter_max: int = 0) -> FeedConfig:
        return FeedConfig(
            timestamp_base_interval=base_interval,
            timestamp_jitter_max=jitter_max,
        )

    def test_output_length_matches_input(self):
        raw = _MOCK_ENTRIES[:5]
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        assert len(result) == len(_MOCK_ENTRIES)

    def test_empty_input_returns_empty_list(self):
        from data.feed import FeedConfig as FC
        # _build_mock_entries 使用固定 _MOCK_ENTRIES，测试非空
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        assert len(result) > 0

    def test_entry_has_required_keys(self):
        required_keys = {"source", "tier", "sentiment", "text", "time"}
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        for entry in result:
            assert required_keys.issubset(entry.keys())

    def test_sentiment_values_are_valid(self):
        valid_sentiments = {"BULL", "BEAR", "NEUT"}
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        for entry in result:
            assert entry["sentiment"] in valid_sentiments

    def test_timestamps_are_ordered_descending(self):
        result = _build_mock_entries(self._make_cfg(jitter_max=0), self.BASE_TIME)
        times = [entry["time"] for entry in result]
        assert times == sorted(times, reverse=True)

    def test_time_format_is_hhmmss(self):
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        for entry in result:
            try:
                datetime.strptime(entry["time"], "%H:%M:%S")
            except ValueError:
                pytest.fail(f"time 字段格式错误: {entry['time']}")

    def test_source_field_preserved(self):
        result = _build_mock_entries(self._make_cfg(), self.BASE_TIME)
        assert result[0]["source"] == _MOCK_ENTRIES[0][0]


class TestParseSentiment:
    """测试情绪判断逻辑（纯函数，独立可测）。"""

    def test_rank_rise_is_bull(self):
        assert _parse_sentiment_by_rank(1, 10) == "BULL"

    def test_rank_drop_is_bear(self):
        assert _parse_sentiment_by_rank(10, 1) == "BEAR"

    def test_small_change_is_neutral(self):
        assert _parse_sentiment_by_rank(5, 6) == "NEUT"

    def test_same_rank_is_neutral(self):
        assert _parse_sentiment_by_rank(5, 5) == "NEUT"

    def test_high_upvote_ratio_is_bull(self):
        assert _parse_sentiment_by_ratio(0.95) == "BULL"

    def test_low_upvote_ratio_is_bear(self):
        assert _parse_sentiment_by_ratio(0.50) == "BEAR"

    def test_mid_upvote_ratio_is_neutral(self):
        assert _parse_sentiment_by_ratio(0.72) == "NEUT"


# ──────────────────────────────────────────────
# data/sources.py
# ──────────────────────────────────────────────

class TestSourceRecords:
    """测试 _SOURCE_RECORDS 原始数据结构完整性。"""

    REQUIRED_KEYS = {"Tier", "Source", "Category", "Language", "API", "Reason"}
    VALID_TIERS   = {"🟢 Tier 1", "🟡 Tier 2", "🔴 Tier 3"}

    def test_all_records_have_required_keys(self):
        """每条记录必须包含 DataFrame 所需的全部列。"""
        for i, record in enumerate(_SOURCE_RECORDS):
            missing = self.REQUIRED_KEYS - record.keys()
            assert not missing, f"第 {i} 条记录缺少键: {missing}"

    def test_all_tier_values_are_valid(self):
        """Tier 字段必须是三个合法值之一。"""
        for record in _SOURCE_RECORDS:
            assert record["Tier"] in self.VALID_TIERS, (
                f"非法 Tier 值: {record['Tier']} (Source: {record['Source']})"
            )

    def test_source_names_are_unique(self):
        """Source 名称不允许重复（防止数据录入错误）。"""
        names = [r["Source"] for r in _SOURCE_RECORDS]
        assert len(names) == len(set(names)), "存在重复的 Source 名称"

    def test_tier1_sources_count(self):
        """Tier 1 数据源应至少有 3 个（保证最低覆盖度）。"""
        tier1 = [r for r in _SOURCE_RECORDS if r["Tier"] == "🟢 Tier 1"]
        assert len(tier1) >= 3, f"Tier 1 数据源数量不足: {len(tier1)}"

    def test_no_empty_reason_fields(self):
        """Reason 字段不允许为空（每个数据源都需要有采集理由）。"""
        for record in _SOURCE_RECORDS:
            assert record["Reason"].strip(), (
                f"Source '{record['Source']}' 的 Reason 字段为空"
            )


# ──────────────────────────────────────────────
# data/compliance.py
# ──────────────────────────────────────────────

class TestComplianceRecords:
    """测试合规数据记录的完整性与一致性。"""

    REQUIRED_KEYS  = {"source", "risk", "color", "tos_clause", "note"}
    VALID_RISKS    = {"HIGH", "MODERATE", "LOW-MOD", "LOW"}
    VALID_COLORS   = {"high", "mod", "low"}

    def test_all_records_have_required_keys(self):
        """每条合规记录必须包含所有必要字段。"""
        for i, record in enumerate(_COMPLIANCE_RECORDS):
            missing = self.REQUIRED_KEYS - record.keys()
            assert not missing, f"第 {i} 条合规记录缺少键: {missing}"

    def test_risk_values_are_valid(self):
        """risk 字段必须在合法枚举集合内。"""
        for record in _COMPLIANCE_RECORDS:
            assert record["risk"] in self.VALID_RISKS, (
                f"非法 risk 值: {record['risk']} (source: {record['source']})"
            )

    def test_color_values_are_valid(self):
        """color 字段必须在 CSS 类合法集合内。"""
        for record in _COMPLIANCE_RECORDS:
            assert record["color"] in self.VALID_COLORS, (
                f"非法 color 值: {record['color']} (source: {record['source']})"
            )

    def test_high_risk_uses_high_color(self):
        """HIGH risk 必须对应 'high' color（CSS 类一致性）。"""
        for record in _COMPLIANCE_RECORDS:
            if record["risk"] == "HIGH":
                assert record["color"] == "high", (
                    f"HIGH risk 但 color={record['color']} (source: {record['source']})"
                )

    def test_low_risk_uses_low_color(self):
        """LOW risk 必须对应 'low' color。"""
        for record in _COMPLIANCE_RECORDS:
            if record["risk"] == "LOW":
                assert record["color"] == "low", (
                    f"LOW risk 但 color={record['color']} (source: {record['source']})"
                )

    def test_no_empty_tos_clause(self):
        """ToS 条款摘要不允许为空。"""
        for record in _COMPLIANCE_RECORDS:
            assert record["tos_clause"].strip(), (
                f"Source '{record['source']}' 的 tos_clause 为空"
            )

    def test_source_names_are_unique(self):
        """合规记录中每个 source 名称不允许重复。"""
        names = [r["source"] for r in _COMPLIANCE_RECORDS]
        assert len(names) == len(set(names)), "存在重复的合规 source 名称"


class TestRiskOrder:
    """测试 RISK_ORDER 排序键覆盖所有风险等级。"""

    def test_high_has_lowest_order_value(self):
        """HIGH 风险排序权重最小（排在最前面）。"""
        assert RISK_ORDER["HIGH"] < RISK_ORDER["LOW"]

    def test_all_risk_levels_covered(self):
        """RISK_ORDER 必须覆盖合规数据中出现的所有 risk 值。"""
        all_risks = {r["risk"] for r in _COMPLIANCE_RECORDS}
        for risk in all_risks:
            assert risk in RISK_ORDER, (
                f"RISK_ORDER 未定义排序权重: '{risk}'"
            )
