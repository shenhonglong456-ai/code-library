# 乾江盛世 AI运营系统 — Claude Code 项目规则

## 项目概述
乾江盛世科技的AI驱动全业务运营系统。7条业务线（A转运仓/B退货/C软件/D跨境Ozon/E AI服务/F小程序公众号/G AI代运营），32个自研Skill覆盖从情报→内容→分发→转化→开发→运营的全链路。

## 核心规则

### 业务红线
- **B线快递老板端所有内容不能提及"软件""系统""技术"** — 只讲赚钱/省钱/方法
- **B线电商端可以讲产品功能**
- **0.1%不确定就问Rita（朱总）** — 不猜业务逻辑

### 全链路操作手册
详见 `03-Skills定义/00-Skills使用指南-全链路操作手册.md`，包含6条流水线的完整使用方式。

### 开发链路自动闭环
当用户说"我要开发XXX"时，自动按以下顺序执行（每步完成后自动进入下一步）：
1. requirement-analyzer → 需求分析
2. prd-generator → PRD文档
3. architecture-designer → 技术方案
4. dev-workflow → 编码+测试
5. code-audit → 代码审查（有🔴回到4修改）
6. 冒烟测试 → 截图+bug自动修复
7. doc-generator → 文档生成

### 内容链路自动闭环
当用户说"根据情报写内容"时，自动串联：
content-planner → copywriter → xhs-image-gen/video-producer → style-manager全程管控

### Skill复盘机制
每个新建/修改的Skill必须：
1. 找真实场景做demo测试
2. 对比实际输出 vs 预期
3. 有差异自动修复
4. 再跑一次验证通过

### LibTV使用规则
- 文生视频：**Seedance 2.0**（必须指定）
- 生图：**Gemini 3.1 Pro**
- 每个独立视频 = 新画布（change_project → create_session）
- 同一视频多镜头 = 同一画布

### 情报系统
- 配置文件：`config/intel-scan-config-v2.json`（7线200+关键词）
- 主脚本：`scripts/daily-intel-briefing.py`（V2，五维分析+重要等级）
- crontab：每天07:30自动执行
- 抓取工具优先级：Firecrawl → Tavily → Perplexity → web-access CDP → 简单HTTP

### 关键文件位置
| 文件 | 路径 |
|------|------|
| Skills使用指南 | `03-Skills定义/00-Skills使用指南-全链路操作手册.md` |
| B线话术体系 | `04-业务线/B-退货软件/B线话术体系-2026-03-31定稿.md` |
| 情报配置V2 | `config/intel-scan-config-v2.json` |
| 情报脚本 | `scripts/daily-intel-briefing.py` |
| API Keys | `scripts/.env` |
| 品牌素材 | `03-品牌素材/`（Logo+二维码+品牌色） |
| 小程序SOP | `08-学习笔记/微信小程序产品打造_从0到1完整SOP.md` |
| 需求挖掘报告 | `新商业布局/03-行业案例/` |
| 公司知识库 | `03-Skills定义/company-context-manager/knowledge/` |

### 飞书配置
- 小龙虾bot App ID: `cli_a93d4e14f9fa5bb5`
- 管理群: `oc_fe5d3d2dfe6bb865c5d00cd168bd4146`
- 员工群: `oc_f72c4a469459f3b8a7ced24747708293`
- 群消息用直连API，不走lark-cli

### 团队
| 姓名 | 职务 |
|------|------|
| 孟奇 | 老板（最终决策） |
| 朱总（朱成成/Rita） | 管理层 |
| 申洪龙 | 市场部经理 |
| 孟祥硕（路涛） | 运营负责人 |
| 张春平 | 客服主管 |
| 彭涛 | 产品技术负责人 |
