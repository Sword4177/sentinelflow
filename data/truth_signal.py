"""
sentinelflow/data/truth_signal.py
─────────────────────────────────────────────────────────
Truth Signal 数据层

将 HTML 中硬编码的 JS 数据提取为 Python TypedDict，
使数据与渲染逻辑解耦，未来接入真实爬虫只需替换此文件。

当前状态：Mock 数据（手动整理，涵盖 2025-01 至 2026-04）
下一步：接入 Truth Social 爬虫 + yfinance 自动对齐市场数据
─────────────────────────────────────────────────────────
"""
import logging
from typing import TypedDict

import streamlit as st

logger = logging.getLogger(__name__)


class TruthEvent(TypedDict):
    """单条 Truth Social 发帖及其市场影响记录。"""
    id:       int    # 唯一标识
    tag:      str    # 分类: "trade" | "crypto" | "fed" | "econ" | "geopolitical"
    date:     str    # 展示日期，如 "Jan 20, 2025"
    month:    str    # 图表对齐月份，如 "2025-01"
    spx:      float  # S&P 500 T+1 日涨跌幅（%）
    btc:      float  # BTC T+1 日涨跌幅（%）
    spx3:     float  # S&P 500 T+3 日涨跌幅（%）
    btc3:     float  # BTC T+3 日涨跌幅（%）
    sb:       int    # S&P 500 发帖前收盘价
    sa:       int    # S&P 500 发帖后收盘价
    bb:       int    # BTC 发帖前价格（USD）
    ba:       int    # BTC 发帖后价格（USD）
    text:     str    # 原文摘录
    analysis: str    # 市场影响分析


# ──────────────────────────────────────────────
# 核心数据记录（28 条，2025-01 ~ 2026-04）
# 最后更新：2026-04-24
# ──────────────────────────────────────────────
_EVENTS: list[TruthEvent] = [
    {
        "id": 1, "tag": "crypto", "date": "Jan 20, 2025", "month": "2025-01",
        "spx": 1.4, "btc": 5.2, "spx3": 2.1, "btc3": 8.4, "sb": 4868, "sa": 4936, "bb": 98000, "ba": 103100,
        "text": '"Day 1: Signed Executive Order on digital assets. America will be the crypto capital of the world!"',
        "analysis": "Inaugural crypto EO on Day 1. Bitcoin surged past $100K; S&P rallied on broad optimism. The executive order directed agencies to promote dollar-backed stablecoins and protect the right to self-custody. Strongest single-day BTC move of Q1 2025.",
    },
    {
        "id": 2, "tag": "econ", "date": "Jan 23, 2025", "month": "2025-01",
        "spx": 0.5, "btc": 2.1, "spx3": 1.2, "btc3": 3.8, "sb": 4975, "sa": 5000, "bb": 102000, "ba": 104100,
        "text": '"Just announced: $500 BILLION in AI infrastructure investment. Stargate is born. America leads the world!"',
        "analysis": "Stargate AI initiative: a $500B joint venture between OpenAI, SoftBank, and Oracle. Tech sector led gains with Nvidia up 4%+. BTC followed risk-on sentiment as AI narrative boosted broader tech enthusiasm.",
    },
    {
        "id": 3, "tag": "trade", "date": "Feb 1, 2025", "month": "2025-02",
        "spx": -1.8, "btc": -4.5, "spx3": -2.9, "btc3": -7.2, "sb": 5954, "sa": 5847, "bb": 103000, "ba": 98400,
        "text": '"25% Tariffs on Canada and Mexico. 10% on China. EFFECTIVE IMMEDIATELY. America First!"',
        "analysis": "Surprise tariff shock on all three major trade partners simultaneously. Markets had priced in gradual escalation; the simultaneous announcement triggered panic selling. BTC dropped sharply as traders fled to USD.",
    },
    {
        "id": 4, "tag": "trade", "date": "Feb 3, 2025", "month": "2025-02",
        "spx": 1.2, "btc": 3.8, "spx3": 1.9, "btc3": 5.1, "sb": 5847, "sa": 5917, "bb": 98400, "ba": 102100,
        "text": '"Just spoke with PM Trudeau. Canada and Mexico tariffs PAUSED for 30 days. Great progress!"',
        "analysis": "30-day tariff pause on Canada/Mexico announced after emergency calls. Markets interpreted this as a negotiating tactic. BTC recovered strongly as risk appetite returned.",
    },
    {
        "id": 5, "tag": "trade", "date": "Mar 4, 2025", "month": "2025-03",
        "spx": -1.4, "btc": -3.2, "spx3": -2.3, "btc3": -5.8, "sb": 5800, "sa": 5719, "bb": 90000, "ba": 87100,
        "text": '"Canada and Mexico tariffs are BACK ON. No more extensions. The time for talk is over."',
        "analysis": "Tariff reimposition after failed negotiations. Markets had priced in a second extension; the reversal triggered fresh sell-off. Auto sector hit hardest with Ford and GM falling 4-6%.",
    },
    {
        "id": 6, "tag": "crypto", "date": "Mar 7, 2025", "month": "2025-03",
        "spx": 0.3, "btc": 12.8, "spx3": 0.8, "btc3": 18.4, "sb": 5719, "sa": 5736, "bb": 87100, "ba": 98300,
        "text": '"Just signed Executive Order establishing the STRATEGIC BITCOIN RESERVE. America will HODL!"',
        "analysis": "Historic Strategic Bitcoin Reserve EO. The US government officially began acquiring BTC as a reserve asset. Crypto market cap added $400B+ in 48 hours. Nation-state FOMO narrative immediately triggered globally.",
    },
    {
        "id": 7, "tag": "trade", "date": "Apr 2, 2025", "month": "2025-04",
        "spx": -4.84, "btc": -6.5, "spx3": -8.9, "btc3": -11.2, "sb": 5580, "sa": 5310, "bb": 85000, "ba": 79500,
        "text": '"LIBERATION DAY is here. Baseline 10% tariff on ALL imports. Reciprocal tariffs on 90+ countries. America is finally free!"',
        "analysis": "Liberation Day — the largest tariff shock in modern history. S&P suffered its worst week since the COVID crash. VIX spiked above 40. The IMF immediately revised global growth forecasts downward by 0.5%.",
    },
    {
        "id": 8, "tag": "trade", "date": "Apr 9, 2025", "month": "2025-04",
        "spx": 9.52, "btc": 8.2, "spx3": 14.1, "btc3": 12.8, "sb": 5110, "sa": 5596, "bb": 79500, "ba": 86000,
        "text": '"I have authorized a 90-DAY PAUSE on reciprocal tariffs for all countries except China. BE COOL!"',
        "analysis": "90-day tariff pause triggered the largest single-day S&P gain since 2020. This post added approximately $2.4 trillion in market cap to global equities within hours — the fastest wealth creation from a single social media post in history.",
    },
    {
        "id": 9, "tag": "trade", "date": "May 12, 2025", "month": "2025-05",
        "spx": 3.3, "btc": 5.1, "spx3": 4.8, "btc3": 7.3, "sb": 5180, "sa": 5351, "bb": 96000, "ba": 100900,
        "text": '"GREAT progress with China! Agreed on 90-day trade truce. Tariffs reduced to 30% while we negotiate a BIG deal!"',
        "analysis": "US-China trade truce announced after Geneva talks. Tariffs reduced from 145% to 30% for 90 days. BTC crossed $100K again on risk-on wave. Apple gained 6% on reduced manufacturing cost concerns.",
    },
    {
        "id": 10, "tag": "econ", "date": "Jul 4, 2025", "month": "2025-07",
        "spx": 0.8, "btc": 2.3, "spx3": 1.4, "btc3": 3.9, "sb": 5580, "sa": 5625, "bb": 115000, "ba": 117600,
        "text": '"Just signed the ONE BIG BEAUTIFUL BILL into law! Massive tax cuts for ALL Americans! Happy Independence Day!"',
        "analysis": "The One Big Beautiful Bill: extended 2017 TCJA tax cuts. Markets modestly positive but deficit concerns (CBO projected +$3.8T over 10 years) limited the rally. Bond yields rose 12bps on deficit fears.",
    },
    {
        "id": 11, "tag": "fed", "date": "Aug 15, 2025", "month": "2025-08",
        "spx": -0.9, "btc": -2.1, "spx3": -1.8, "btc3": -4.2, "sb": 5700, "sa": 5649, "bb": 100000, "ba": 97900,
        "text": '"The Fed\'s Jerome Powell is a FOOL. Rates should be at ZERO. Cut NOW or I\'ll find someone who will!"',
        "analysis": "Direct public threat to replace Fed Chair Powell. Markets rattled by Fed independence concerns — euro and yen strengthened against the dollar as investors fled US assets. Legal scholars noted the President has limited authority to remove a sitting Fed Chair.",
    },
    {
        "id": 12, "tag": "fed", "date": "Sep 18, 2025", "month": "2025-09",
        "spx": 1.7, "btc": 4.2, "spx3": 2.9, "btc3": 6.8, "sb": 5620, "sa": 5715, "bb": 68000, "ba": 70900,
        "text": '"The Fed has FINALLY cut rates. Should have done it sooner but better late than never. Markets will BOOM!"',
        "analysis": "Fed 25bps rate cut to 4.00-4.25% range. Both S&P and BTC rallied. Powell emphasized the decision was data-driven — a pointed response to months of presidential pressure.",
    },
    {
        "id": 13, "tag": "crypto", "date": "Nov 3, 2025", "month": "2025-11",
        "spx": 0.6, "btc": 7.4, "spx3": 1.2, "btc3": 12.1, "sb": 5850, "sa": 5885, "bb": 88000, "ba": 94500,
        "text": '"The US Bitcoin Reserve now holds 200,000 BTC. We are the LARGEST Bitcoin holder in the world. WINNING!"',
        "analysis": "Government Bitcoin accumulation disclosure. BTC surged on supply squeeze narrative — with the US holding ~1% of total supply, the market perceived a structural demand floor.",
    },
    {
        "id": 14, "tag": "econ", "date": "Jan 20, 2026", "month": "2026-01",
        "spx": 0.4, "btc": 1.8, "spx3": 0.9, "btc3": 2.4, "sb": 6090, "sa": 6114, "bb": 103000, "ba": 104800,
        "text": '"ONE YEAR IN OFFICE! Stock market up 20%, Bitcoin up 40%, unemployment at record lows. PROMISES MADE, PROMISES KEPT!"',
        "analysis": "One-year anniversary post. Markets modestly positive. However, inflation remained elevated at 3.1%, trade deficit had widened, and interest payments on national debt reached $1.2T annually.",
    },
    {
        "id": 15, "tag": "trade", "date": "Feb 10, 2026", "month": "2026-02",
        "spx": -2.1, "btc": -3.5, "spx3": -3.8, "btc3": -6.2, "sb": 6000, "sa": 5874, "bb": 92000, "ba": 88800,
        "text": '"25% tariffs on ALL European Union imports. They have ripped us off for decades. NO MORE!"',
        "analysis": "New EU tariff threat escalated the trade war to Europe. European markets fell 3%+; DAX dropped 4.2%. Airbus canceled $12B in US engine orders.",
    },
    {
        "id": 16, "tag": "trade", "date": "Mar 12, 2026", "month": "2026-03",
        "spx": -1.8, "btc": -2.8, "spx3": -3.1, "btc3": -4.9, "sb": 5780, "sa": 5676, "bb": 86000, "ba": 83600,
        "text": '"The EU refuses to negotiate fairly. Tariffs going to 35%. Steel and aluminum at 50%. America FIRST!"',
        "analysis": "Tariff escalation on EU after failed negotiations. Boeing shares dropped 5% on fears of retaliatory EU aircraft procurement policies. Analysts called this the beginning of Trade War Phase 2.",
    },
    {
        "id": 17, "tag": "trade", "date": "Apr 2, 2026", "month": "2026-04",
        "spx": -4.2, "btc": -5.8, "spx3": -7.1, "btc3": -9.4, "sb": 5612, "sa": 5376, "bb": 82000, "ba": 77200,
        "text": '"LIBERATION DAY 2.0! New global tariff wave on 60 countries. This time it\'s PERMANENT. America will be rich again!"',
        "analysis": "Second Liberation Day. The word PERMANENT triggered outsized panic. BTC fell below $80K for the first time since early 2025. The IMF issued an emergency statement warning of global recession risk.",
    },
    {
        "id": 18, "tag": "trade", "date": "Apr 9, 2026", "month": "2026-04",
        "spx": 7.2, "btc": 6.4, "spx3": 10.8, "btc3": 9.7, "sb": 5210, "sa": 5585, "bb": 77200, "ba": 82100,
        "text": '"Pausing new tariffs for 60 days to allow negotiations. Many countries calling, want to make deals. WINNING!"',
        "analysis": "Partial tariff pause déjà vu — exactly 365 days after the original Apr 9, 2025 pause. Second-largest single-day S&P gain in the dataset. Algorithmic traders had positioned for the bounce in advance.",
    },
    # ── 新增事件（2026-04-24 补录）──
    {
        "id": 19, "tag": "fed", "date": "Mar 12, 2025", "month": "2025-03",
        "spx": -0.6, "btc": -1.8, "spx3": -1.2, "btc3": -3.1, "sb": 5790, "sa": 5755, "bb": 88000, "ba": 86400,
        "text": '"Fed Chair Powell is making a BIG MISTAKE. Interest Rates should be cut NOW. He is always too late!"',
        "analysis": "Trump's public pressure campaign on Powell triggered Fed independence concerns. Gold rose $28/oz as investors sought safe havens. DXY fell 0.6% on dollar credibility fears. 10-year Treasury yields dropped 4bps. Legal scholars noted the president has limited authority to remove a sitting Fed Chair without cause — the same debate that would resurface in August 2025.",
    },
    {
        "id": 20, "tag": "trade", "date": "Oct 10, 2025", "month": "2025-10",
        "spx": -2.7, "btc": -4.1, "spx3": -3.8, "btc3": -5.9, "sb": 6800, "sa": 6616, "bb": 107000, "ba": 102600,
        "text": '"China is becoming very hostile. They control rare earth metals and are holding the world CAPTIVE. Massive tariff increase on Chinese products coming!"',
        "analysis": "Single post wiped $2 trillion from global markets — the largest single-day loss since Liberation Day. Nvidia lost 5% ($229B market cap); AMD fell 8%; Apple shed 3%. 424 of 500 S&P members closed red. China had tightened rare earth export controls overnight, and Trump's post came at the worst possible moment. US rare earth suppliers MP Materials (+11%) and USA Rare Earth (+15%) were the only winners.",
    },
    {
        "id": 21, "tag": "trade", "date": "Oct 12, 2025", "month": "2025-10",
        "spx": 1.0, "btc": 2.3, "spx3": 1.8, "btc3": 3.7, "sb": 6616, "sa": 6682, "bb": 102600, "ba": 104900,
        "text": '"Don\'t worry about China, it will all be fine! Highly respected President Xi just had a bad moment. The US wants to help China, not hurt it."',
        "analysis": "Conciliatory reversal just 48 hours after the rare earth shock. S&P 500 futures climbed 0.9-1.1%; Nasdaq futures surged 1.2-1.6%. The pattern — shock post followed by reassurance post — had become a recognizable Trump playbook by late 2025. Algorithmic traders were now pre-positioning for the rebound leg as soon as the initial crash began.",
    },
    {
        "id": 22, "tag": "trade", "date": "Jan 13, 2026", "month": "2026-01",
        "spx": -0.8, "btc": -1.5, "spx3": -1.4, "btc3": -2.8, "sb": 6960, "sa": 6904, "bb": 97000, "ba": 95600,
        "text": '"Effective immediately, any country doing business with the Islamic Republic of Iran will pay a Tariff of 25%. This Order is final and conclusive."',
        "analysis": "Secondary tariff shock targeting Iran's trading partners — a novel use of tariffs as a geopolitical weapon rather than a trade tool. Markets reacted with moderate concern as the policy scope was unclear. Energy stocks initially rallied on Iran isolation thesis before retreating. No formal White House documentation accompanied the post, raising legal ambiguity about enforcement.",
    },
    {
        "id": 23, "tag": "geopolitical", "date": "Mar 23, 2026", "month": "2026-03",
        "spx": 0.6, "btc": 1.2, "spx3": 1.1, "btc3": 2.0, "sb": 6760, "sa": 6801, "bb": 84000, "ba": 85000,
        "text": '"Just had very PRODUCTIVE talks with Iran. Progress is being made. A deal is possible!"',
        "analysis": "Crude oil prices plunged on the peace signal — the first positive Iran post since the conflict began. Energy sector fell 2% as oil risk premium compressed. BTC and equities gained on risk-on sentiment. However, Trump officials privately warned that the post was undermining formal negotiation channels, a pattern that would repeat through April.",
    },
    {
        "id": 24, "tag": "geopolitical", "date": "Apr 5, 2026", "month": "2026-04",
        "spx": -1.5, "btc": -2.8, "spx3": -2.1, "btc3": -4.2, "sb": 5680, "sa": 5595, "bb": 79000, "ba": 76800,
        "text": '"Open the Fuckin\' Strait or we will bomb your bridges, power plants, and everything else. A whole civilization will die tonight if the Hormuz is not OPENED!"',
        "analysis": "Easter Sunday post threatening Iranian infrastructure — the most incendiary presidential social media post ever recorded. Oil prices spiked immediately; Brent crude surged toward $106. Markets opened sharply lower on Monday. The post was verified by fact-checkers and major outlets. US officials privately said the post complicated ceasefire negotiations. VIX spiked to 28.",
    },
    {
        "id": 25, "tag": "trade", "date": "Apr 8, 2026", "month": "2026-04",
        "spx": 1.8, "btc": 3.2, "spx3": 3.1, "btc3": 5.4, "sb": 5595, "sa": 5696, "bb": 76800, "ba": 79200,
        "text": '"A Country supplying Military Weapons to Iran will be immediately tariffed 50% on any and all goods. Effective IMMEDIATELY. No exclusions or exemptions!"',
        "analysis": "Tariff threat on Iran weapon suppliers combined with a simultaneous two-week US-Iran ceasefire announcement. The ceasefire dominated market reaction, sending S&P futures higher. The 50% weapon-supplier tariff was largely ignored in the rally as traders focused on the de-escalation signal. S&P 500 posted its best weekly gain since November 2025.",
    },
    {
        "id": 26, "tag": "econ", "date": "Apr 10, 2026", "month": "2026-04",
        "spx": -0.1, "btc": -0.5, "spx3": 0.8, "btc3": 1.4, "sb": 6817, "sa": 6810, "bb": 79500, "ba": 79100,
        "text": '"Palantir Technologies (PLTR) has proven to have great warfighting capabilities and equipment. Just ask our enemies!!! President DJT."',
        "analysis": "Direct presidential endorsement of a defense contractor with active government contracts — a market manipulation concern raised by analysts and lawmakers. PLTR spiked intraday despite being on track for a 13% weekly loss. The post raised questions about insider information after suspicious options activity preceded the announcement. Iran-related posts the same day calling out 'short term extortion' saw minimal market reaction.",
    },
    {
        "id": 27, "tag": "geopolitical", "date": "Apr 23, 2026", "month": "2026-04",
        "spx": 0.2, "btc": 0.8, "spx3": 0.9, "btc3": 1.5, "sb": 7020, "sa": 7034, "bb": 93000, "ba": 93700,
        "text": '"Israel and Lebanon have agreed to extend their ceasefire by THREE WEEKS. Great news for the Middle East and the World!"',
        "analysis": "Israel-Lebanon ceasefire extension announcement. S&P 500 futures were little changed — markets had largely priced in de-escalation hopes. Nasdaq futures rose 0.3% on tech relief. The ceasefire extension was seen as a positive step but insufficient to resolve the broader Strait of Hormuz standoff, keeping geopolitical risk premium elevated.",
    },
    {
        "id": 28, "tag": "econ", "date": "Apr 24, 2026", "month": "2026-04",
        "spx": 0.8, "btc": 1.4, "spx3": 1.2, "btc3": 2.1, "sb": 7100, "sa": 7165, "bb": 93000, "ba": 94300,
        "text": '"The DOJ has dropped its probe into Chair Powell. Markets are going UP like a ROCKET. Intel had INCREDIBLE earnings. AI is the future!"',
        "analysis": "DOJ dropped criminal probe into Fed Chair Powell, removing a key uncertainty and clearing the path for Trump's Fed pick Kevin Warsh. Combined with Intel's blockbuster Q1 earnings — the stock's biggest beat in years — the S&P 500 and Nasdaq hit new all-time closing highs. Nvidia crossed $5 trillion market cap again. AMD surged 13%, Qualcomm gained 10%. The day marked a peak in AI optimism amid the ongoing Iran conflict.",
    },
]


@st.cache_data
def get_truth_events() -> list[TruthEvent]:
    """
    返回所有 Truth Social 市场事件记录。

    降级策略：
        构建失败时返回空列表，Module D 显示空状态，不崩溃。

    Returns:
        TruthEvent 列表，按时间顺序排列（最早在前）。
    """
    try:
        logger.debug("Truth Signal 数据加载完成，共 %d 条事件", len(_EVENTS))
        return list(_EVENTS)
    except Exception as exc:
        logger.error("Truth Signal 数据加载失败: %s", exc, exc_info=True)
        return []


def get_summary_stats(events: list[TruthEvent]) -> dict:
    """
    计算事件集合的汇总统计数据，供 Module D 顶部 Metric 卡片使用。

    Args:
        events: TruthEvent 列表。

    Returns:
        包含 avg_neg_spx / avg_pos_spx / max_btc_gain / total 的字典。
    """
    if not events:
        return {"avg_neg_spx": 0.0, "avg_pos_spx": 0.0, "max_btc_gain": 0.0, "total": 0}

    neg_spx = [e["spx"] for e in events if e["spx"] < 0]
    pos_spx = [e["spx"] for e in events if e["spx"] > 0]

    return {
        "avg_neg_spx": round(sum(neg_spx) / len(neg_spx), 2) if neg_spx else 0.0,
        "avg_pos_spx": round(sum(pos_spx) / len(pos_spx), 2) if pos_spx else 0.0,
        "max_btc_gain": round(max(e["btc"] for e in events), 1),
        "total": len(events),
    }
