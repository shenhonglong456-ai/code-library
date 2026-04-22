#!/usr/bin/env python3
"""
乾江盛世 - 竞品追踪工具 (competitor-tracker)

功能: 按业务线扫描竞品动态 → Claude分析 → 生成周报 → 存档 → 飞书推送
触发: 每周一自动 or Rita手动指定

用法:
  python3 competitor-scan.py                    # 扫描所有业务线竞品
  python3 competitor-scan.py --line B_退货       # 只扫B线竞品
  python3 competitor-scan.py --competitor 聚水潭  # 只查某个竞品
  python3 competitor-scan.py --no-push --dry-run # 试运行
"""

import json
import os
import sys
import datetime
import logging
import re
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List

# ─── 路径配置 ───
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "06-知识库" / "竞品档案"
PROMPT_PATH = SKILL_DIR / "prompts" / "weekly-report.md"
LOG_DIR = PROJECT_ROOT / "scripts" / "logs"

# ─── 加载 .env ───
def load_env():
    env_path = PROJECT_ROOT / "scripts" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if val and key.strip():
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

# ─── API Keys ───
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
PERPLEXITY_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_GROUP = os.environ.get("FEISHU_MANAGEMENT_GROUP", "")

# ─── 日志 ───
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"competitor-{datetime.date.today()}.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("competitor")

# ─── 竞品清单 ───
COMPETITORS = {
    "B_退货": {
        "competitors": [
            {"name": "菜鸟裹裹", "queries": ["菜鸟裹裹 退货 最新动态", "菜鸟 派费规则 变化"]},
            {"name": "顺丰退货仓", "queries": ["顺丰 退货仓 服务 动态", "顺丰 逆向物流 新闻"]},
            {"name": "聚水潭", "queries": ["聚水潭 产品更新 2026", "聚水潭 退货功能 新增"]},
            {"name": "万里牛", "queries": ["万里牛 ERP 更新 2026", "万里牛 逆向物流"]},
            {"name": "退货SaaS创业公司", "queries": ["退货管理 SaaS 融资 2026", "逆向物流 创业公司 新闻"]},
        ]
    },
    "A_转运仓": {
        "competitors": [
            {"name": "主流云仓服务商", "queries": ["云仓服务商 动态 2026", "一件代发 平台 新规"]},
        ]
    },
    "C_软件": {
        "competitors": [
            {"name": "聚水潭", "queries": ["聚水潭 功能更新 定价 2026"]},
            {"name": "万里牛", "queries": ["万里牛 新功能 2026"]},
            {"name": "旺店通", "queries": ["旺店通 ERP WMS 2026"]},
            {"name": "物流SaaS新玩家", "queries": ["物流SaaS 融资 新公司 2026"]},
        ]
    },
    "D_跨境Ozon": {
        "competitors": [
            {"name": "俄罗斯海外仓", "queries": ["俄罗斯 海外仓 服务商 动态 2026"]},
            {"name": "Ozon代运营", "queries": ["Ozon 代运营 公司 动态 2026"]},
        ]
    },
    "E_AI服务": {
        "competitors": [
            {"name": "AI企业服务公司", "queries": ["AI企业服务 公司 动态 融资 2026"]},
            {"name": "AI培训机构", "queries": ["AI培训 机构 新课程 2026"]},
        ]
    },
    "F_小程序公众号": {
        "competitors": [
            {"name": "热门工具小程序", "queries": ["微信小程序 工具类 热门 2026"]},
            {"name": "快递行业小程序", "queries": ["快递 小程序 新上线 2026"]},
        ]
    },
    "G_AI代运营": {
        "competitors": [
            {"name": "AI代运营公司", "queries": ["AI代运营 公司 服务 案例 2026"]},
            {"name": "MCN转型", "queries": ["MCN AI转型 内容生产 2026"]},
        ]
    }
}


# ═══════════════════════════════════════════
#  采集: Tavily + Perplexity
# ═══════════════════════════════════════════

def search_tavily(query: str) -> Optional[str]:
    """Tavily搜索"""
    if not TAVILY_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": True
            },
            timeout=30
        )
        data = resp.json()
        answer = data.get("answer", "")
        results = data.get("results", [])
        snippets = "\n".join([f"- {r.get('title','')}: {r.get('content','')[:200]} ({r.get('url','')})" for r in results[:3]])
        return f"综合回答: {answer}\n\n来源:\n{snippets}"
    except Exception as e:
        log.warning(f"Tavily搜索失败 [{query}]: {e}")
        return None


def search_perplexity(query: str) -> Optional[str]:
    """Perplexity搜索"""
    if not PERPLEXITY_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {"role": "user", "content": f"请搜索并总结：{query}。只要最近7天的信息。"}
                ]
            },
            timeout=60
        )
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        log.warning(f"Perplexity搜索失败 [{query}]: {e}")
        return None


def gather_competitor_intel(competitor: Dict) -> Dict:
    """采集单个竞品的情报"""
    name = competitor["name"]
    log.info(f"  🔍 扫描竞品: {name}")

    results = []
    for query in competitor["queries"]:
        tavily_result = search_tavily(query)
        if tavily_result:
            results.append(f"[Tavily] {query}:\n{tavily_result}")

        pplx_result = search_perplexity(query)
        if pplx_result:
            results.append(f"[Perplexity] {query}:\n{pplx_result}")

    return {
        "name": name,
        "raw_intel": "\n\n---\n\n".join(results) if results else "本周无动态"
    }


# ═══════════════════════════════════════════
#  分析: Claude生成周报
# ═══════════════════════════════════════════

def generate_weekly_report(all_intel: Dict[str, List[Dict]]) -> Optional[str]:
    """用Claude汇总生成竞品周报"""
    log.info("🧠 Claude生成竞品周报...")

    if not ANTHROPIC_KEY:
        log.error("未配置ANTHROPIC_API_KEY")
        return None

    prompt_template = ""
    if PROMPT_PATH.exists():
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    # 整理采集内容
    intel_text = ""
    for line_name, competitors in all_intel.items():
        intel_text += f"\n\n## {line_name}\n"
        for comp in competitors:
            intel_text += f"\n### {comp['name']}\n{comp['raw_intel']}\n"

    user_msg = f"""请根据以下本周采集到的竞品信息，生成一份结构化的竞品动态周报。

日期范围: {(datetime.date.today() - datetime.timedelta(days=7)).isoformat()} ~ {datetime.date.today().isoformat()}

--- 采集的竞品情报 ---
{intel_text[:15000]}
--- 采集结束 ---

{prompt_template}"""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": user_msg}]
            },
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        result = data["content"][0]["text"]
        log.info(f"✅ 周报生成完成 ({len(result)}字)")
        return result
    except Exception as e:
        log.error(f"Claude分析失败: {e}")
        return None


# ═══════════════════════════════════════════
#  存档 + 飞书推送
# ═══════════════════════════════════════════

def save_report(report: str) -> Path:
    """保存周报到知识库"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    filepath = KNOWLEDGE_DIR / f"{today}-竞品周报.md"
    filepath.write_text(report, encoding="utf-8")
    log.info(f"💾 周报已存档: {filepath}")
    return filepath


def get_feishu_token() -> str:
    data = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    ).json()
    return data.get("tenant_access_token", "")


def push_to_feishu(report: str, dry_run=False):
    """推送精简版到飞书"""
    if not all([FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_GROUP]):
        log.warning("飞书配置不完整，跳过推送")
        return

    # 提取"本周要闻"部分
    highlights = []
    in_highlights = False
    for line in report.split("\n"):
        if "本周要闻" in line or "必看" in line:
            in_highlights = True
            continue
        if in_highlights and line.startswith("##"):
            break
        if in_highlights and line.strip().startswith("-"):
            highlights.append(line.strip())

    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)

    highlights_text = "\n".join(highlights[:5]) if highlights else "本周竞品无重大动态"

    msg = f"""📊 竞品周报 {week_ago.strftime('%m-%d')} ~ {today.strftime('%m-%d')}

🔴 必看：
{highlights_text}

📋 完整报告已存档到知识库"""

    if dry_run:
        log.info(f"[DRY RUN] 飞书消息:\n{msg}")
        return

    token = get_feishu_token()
    if not token:
        return

    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            params={"receive_id_type": "chat_id"},
            json={
                "receive_id": FEISHU_GROUP,
                "msg_type": "text",
                "content": json.dumps({"text": msg}, ensure_ascii=False)
            },
            timeout=10
        )
        if resp.status_code == 200:
            log.info("📤 飞书推送成功")
        else:
            log.warning(f"飞书推送异常: {resp.status_code}")
    except Exception as e:
        log.error(f"飞书推送失败: {e}")


# ═══════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="乾江盛世 - 竞品追踪工具")
    parser.add_argument("--line", default="", help="只扫描某条业务线，如 B_退货")
    parser.add_argument("--competitor", default="", help="只查某个竞品，如 聚水潭")
    parser.add_argument("--no-push", action="store_true", help="不推送飞书")
    parser.add_argument("--dry-run", action="store_true", help="试运行")
    args = parser.parse_args()

    log.info(f"🚀 竞品扫描启动 | 业务线: {args.line or '全部'} | 竞品: {args.competitor or '全部'}")

    # 采集
    all_intel = {}
    for line_name, line_data in COMPETITORS.items():
        if args.line and args.line not in line_name:
            continue

        log.info(f"\n━━ {line_name} ━━")
        line_results = []

        for comp in line_data["competitors"]:
            if args.competitor and args.competitor not in comp["name"]:
                continue
            result = gather_competitor_intel(comp)
            line_results.append(result)

        if line_results:
            all_intel[line_name] = line_results

    if not all_intel:
        log.warning("未采集到任何竞品信息")
        return

    # 分析
    report = generate_weekly_report(all_intel)
    if not report:
        log.error("周报生成失败")
        return

    # 存档
    save_report(report)

    # 推送
    if not args.no_push:
        push_to_feishu(report, dry_run=args.dry_run)

    log.info("✅ 竞品扫描完成")


if __name__ == "__main__":
    main()
