#!/usr/bin/env python3
"""
乾江盛世 - 情报深度挖掘工具 (deep-crawler)

功能: 对指定URL进行全文抓取 → 五维深度分析 → 存档 → 飞书推送
触发: Rita手动指定（"深挖这个URL" 或 "深挖早报第X条"）

用法:
  python3 deep-crawl.py <url> [--line B_退货] [--no-push] [--dry-run]
  python3 deep-crawl.py <url1> <url2> <url3>  # 批量深挖

依赖:
  - Firecrawl API (FIRECRAWL_API_KEY) 或 MCP
  - Anthropic API (ANTHROPIC_API_KEY) - Claude分析
  - 飞书API (FEISHU_APP_ID/SECRET) - 小龙虾bot推送
"""

import json
import os
import sys
import datetime
import logging
import re
import requests
from pathlib import Path
from typing import Optional

# ─── 路径配置 ───
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent  # files/
KNOWLEDGE_DIR = PROJECT_ROOT / "06-知识库" / "行业动态"
PROMPT_PATH = SKILL_DIR / "prompts" / "analyze-5dim.md"
LOG_DIR = PROJECT_ROOT / "scripts" / "logs"

# ─── 加载 .env (复用情报系统的.env) ───
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
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_GROUP = os.environ.get("FEISHU_MANAGEMENT_GROUP", "")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

# ─── 日志 ───
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"deep-crawl-{datetime.date.today()}.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("deep-crawler")


# ═══════════════════════════════════════════
#  Step 1: 全文抓取
# ═══════════════════════════════════════════

def crawl_url(url: str) -> Optional[str]:
    """用Firecrawl API抓取URL全文内容"""
    log.info(f"🔍 抓取: {url}")

    if not FIRECRAWL_KEY:
        log.warning("未配置FIRECRAWL_API_KEY，尝试简单抓取")
        return simple_fetch(url)

    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "waitFor": 8000
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("success") and data.get("data", {}).get("markdown"):
            content = data["data"]["markdown"]
            title = data["data"].get("metadata", {}).get("title", "未知标题")
            log.info(f"✅ 抓取成功: {title} ({len(content)}字)")
            return content
        else:
            log.warning(f"Firecrawl返回异常: {data}")
            return simple_fetch(url)

    except Exception as e:
        log.error(f"Firecrawl抓取失败: {e}")
        return simple_fetch(url)


def simple_fetch(url: str) -> Optional[str]:
    """简单HTTP抓取作为fallback"""
    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp.raise_for_status()
        # 简单提取正文(去掉HTML标签)
        import re
        text = re.sub(r'<[^>]+>', '', resp.text)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 500:
            log.info(f"✅ 简单抓取成功 ({len(text)}字)")
            return text[:15000]  # 限制长度
        return None
    except Exception as e:
        log.error(f"简单抓取也失败: {e}")
        return None


# ═══════════════════════════════════════════
#  Step 2: 五维深度分析
# ═══════════════════════════════════════════

def analyze_content(content: str, url: str, business_line: str = "") -> Optional[str]:
    """用Claude进行五维深度分析"""
    log.info("🧠 开始五维分析...")

    if not ANTHROPIC_KEY:
        log.error("未配置ANTHROPIC_API_KEY")
        return None

    # 读取分析提示词
    prompt_template = ""
    if PROMPT_PATH.exists():
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    else:
        prompt_template = "请对以下文章进行深度分析，覆盖：业务影响、改进机会、业务发展、战略方向、内容转化五个维度。"

    user_msg = f"""请对以下文章进行五维深度分析。

原文URL: {url}
{f'关联业务线: {business_line}' if business_line else '请自动判断关联的业务线'}

--- 文章内容 ---
{content[:12000]}
--- 文章结束 ---

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
        log.info(f"✅ 分析完成 ({len(result)}字)")
        return result

    except Exception as e:
        log.error(f"Claude分析失败: {e}")
        return None


# ═══════════════════════════════════════════
#  Step 3: 存档
# ═══════════════════════════════════════════

def save_to_knowledge_base(analysis: str, url: str) -> Path:
    """保存分析结果到知识库"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    # 从分析结果中提取标题
    title_match = re.search(r'^#\s+(.+)', analysis, re.MULTILINE)
    if title_match:
        title_slug = title_match.group(1)[:30].strip()
        # 清理文件名
        title_slug = re.sub(r'[^\w\u4e00-\u9fff-]', '', title_slug)
    else:
        title_slug = "深度分析"

    today = datetime.date.today().isoformat()
    filename = f"{today}-{title_slug}.md"
    filepath = KNOWLEDGE_DIR / filename

    # 避免重名
    counter = 1
    while filepath.exists():
        filepath = KNOWLEDGE_DIR / f"{today}-{title_slug}-{counter}.md"
        counter += 1

    filepath.write_text(analysis, encoding="utf-8")
    log.info(f"💾 已存档: {filepath}")
    return filepath


# ═══════════════════════════════════════════
#  Step 4: 飞书推送
# ═══════════════════════════════════════════

def get_feishu_token() -> str:
    """获取飞书 tenant_access_token"""
    data = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    ).json()
    if data and data.get("tenant_access_token"):
        return data["tenant_access_token"]
    log.error(f"获取飞书token失败: {data}")
    return ""


def push_to_feishu(analysis: str, url: str, dry_run=False):
    """推送精简版到飞书管理群"""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET or not FEISHU_GROUP:
        log.warning("飞书配置不完整，跳过推送")
        return

    # 提取精简版内容
    title = "深度分析"
    title_match = re.search(r'^#\s+(.+)', analysis, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()

    # 提取等级
    grade = "⚪常规"
    grade_match = re.search(r'等级[：:]\s*(🔴重大|🟡关注|⚪常规)', analysis)
    if grade_match:
        grade = grade_match.group(1)

    # 提取业务线
    biz_line = ""
    biz_match = re.search(r'关联业务线[：:]\s*(.+)', analysis)
    if biz_match:
        biz_line = biz_match.group(1).strip()

    # 提取核心要点
    points = []
    points_section = re.search(r'核心要点.*?\n((?:[-•]\s*.+\n?)+)', analysis)
    if points_section:
        for line in points_section.group(1).strip().split('\n'):
            line = line.strip().lstrip('-•').strip()
            if line:
                points.append(line)

    # 提取行动建议
    actions = []
    action_section = re.search(r'行动建议.*?\n((?:[-•]\s*.+\n?)+)', analysis)
    if action_section:
        for line in action_section.group(1).strip().split('\n'):
            line = line.strip().lstrip('-•').strip()
            if line:
                actions.append(line)

    # 构建飞书消息
    points_text = "\n".join([f"  {i+1}. {p}" for i, p in enumerate(points[:5])])
    actions_text = "\n".join([f"  • {a}" for a in actions[:3]])

    msg = f"""🔍 深度分析：{title}
等级：{grade} | 业务线：{biz_line}

📌 核心要点：
{points_text}

💡 行动建议：
{actions_text}

🔗 原文：{url}
📄 完整分析已存档到知识库"""

    if dry_run:
        log.info(f"[DRY RUN] 飞书消息:\n{msg}")
        return

    token = get_feishu_token()
    if not token:
        return

    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
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
            log.warning(f"飞书推送异常: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"飞书推送失败: {e}")


# ═══════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════

def deep_crawl(url: str, business_line: str = "", dry_run=False, no_push=False) -> bool:
    """单条URL的完整深挖流程"""
    log.info(f"\n{'='*60}")
    log.info(f"🎯 开始深挖: {url}")
    log.info(f"{'='*60}")

    # Step 1: 抓取
    content = crawl_url(url)
    if not content:
        log.error(f"❌ 抓取失败，跳过: {url}")
        return False

    # Step 2: 分析
    analysis = analyze_content(content, url, business_line)
    if not analysis:
        log.error(f"❌ 分析失败，跳过: {url}")
        return False

    # Step 3: 存档
    filepath = save_to_knowledge_base(analysis, url)

    # Step 4: 推送
    if not no_push:
        push_to_feishu(analysis, url, dry_run=dry_run)

    log.info(f"✅ 深挖完成: {url}")
    log.info(f"   存档位置: {filepath}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="乾江盛世 - 情报深度挖掘工具")
    parser.add_argument("urls", nargs="+", help="要深挖的URL列表")
    parser.add_argument("--line", default="", help="关联业务线，如 B_退货")
    parser.add_argument("--no-push", action="store_true", help="不推送飞书")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际推送")
    args = parser.parse_args()

    log.info(f"🚀 深度挖掘启动 | URLs: {len(args.urls)} | 业务线: {args.line or '自动判断'}")

    success = 0
    for url in args.urls:
        if deep_crawl(url, args.line, args.dry_run, args.no_push):
            success += 1

    log.info(f"\n📊 深挖结果: {success}/{len(args.urls)} 成功")


if __name__ == "__main__":
    main()
