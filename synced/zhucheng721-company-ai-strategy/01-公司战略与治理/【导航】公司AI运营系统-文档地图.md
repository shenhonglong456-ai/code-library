# 乾江盛世 AI运营系统 — 文档导航地图

**最后更新：** 2026-04-03
**规则：** 🟢当前有效 🟡需更新/参考 🔴已过时/被替代
**冲突解决：** CLAUDE.md > 记忆系统 > Skills SKILL.md > 操作手册 > 话术定稿 > 其他文档

---

## ⭐ 总入口（必看）

| 文件 | 说明 |
|------|------|
| 🟢 **CLAUDE.md**（根目录） | 项目规则总纲，所有规则汇总 |
| 🟢 **03-Skills定义/00-Skills使用指南-全链路操作手册.md** | 32个Skill怎么用、7条流水线怎么跑 |
| 🟢 **01-公司战略/Skills建设总计划.md** | 6阶段32个Skill架构图 |

---

## 01-公司战略与治理

| 文件 | 状态 | 说明 |
|------|------|------|
| Skills建设总计划.md | 🟢 | 32个Skill架构，已全部建完 |
| company-context.md | 🟡 | 早期版，应以company-context-manager/knowledge/*.yaml为准 |
| 2026-03-19-业务督办中台设计方案.md | 🟢 | task-supervisor基础 |
| 2026-03-19-ClawTeam落地方案.md | 🟡 | 部分被Skills替代 |
| MetaGPT架构适配分析.md | 🔴 | 被Skills建设总计划替代 |
| 角色体系-融合版.md | 🔴 | 被32个Skill替代 |
| archive/ | 🔴 | 历史归档 |

## 02-市场调研

| 文件 | 状态 | 说明 |
|------|------|------|
| YYYY-MM-DD-每日情报简报.md | 🟢 | V2自动生成（7线五维分析） |
| 情报收集标准流程-SOP.md | 🔴 | 被intel-scanner V2 + config-v2.json替代 |
| 03-13/17/21调研文档 | 🔴 | 早期调研，结论已融入记忆 |

## 03-Skills定义

| 文件 | 状态 | 说明 |
|------|------|------|
| **00-Skills使用指南.md** | 🟢 | 唯一操作手册 |
| 00-Skills调研与标准结构参考.md | 🔴 | 早期调研，已被实际Skill替代 |
| baoyu技能矩阵与选用指南.md | 🟢 | baoyu系列选用 |
| 32个Skill的SKILL.md | 🟢 | 每个Skill的定义 |

## 04-业务线

| 文件 | 状态 | 说明 |
|------|------|------|
| **B-退货/B线话术体系-2026-03-31定稿.md** | 🟢 | B线唯一话术标准 |
| B-退货/B线推广执行方案.md | 🟡 | 部分内容与话术体系不一致 |
| B-退货/B线战略定位与竞品分析.md | 🟡 | 竞品可能过时，以competitor-tracker为准 |
| **video-templates/视频生产双轨方案.md** | 🔴 | **被video-producer Skill替代**（现在是三种模式） |

## 05-内容产出

| 文件 | 状态 | 说明 |
|------|------|------|
| **视频生产双轨方案.md** | 🔴 | 重复+过时，被video-producer替代 |
| **全渠道矩阵运营规划.md** | 🔴 | 缺快手/微博/B站，被schedule-manager替代 |
| **内容生产技能矩阵与视频制作SOP.md** | 🟡 | 参考用，执行以Skills操作手册为准 |
| 模板库/*.md | 🟡 | 内容有效但应与style-manager对齐 |
| YYYY-MM-DD-*/ | 🟢 | 实际产出的内容成品 |

## 06-知识库

| 文件 | 状态 | 说明 |
|------|------|------|
| 行业动态/*.md | 🟢 | deep-crawler存档 |
| 竞品档案/*.md | 🟡 | 早期扫描，以competitor-tracker为准 |

## 07-规范与清单

| 文件 | 状态 | 说明 |
|------|------|------|
| **待做表-全链路搭建任务清单.md** | 🔴 | 严重过时，以master_roadmap记忆为准 |
| 全渠道内容策略层规范.md | 🔴 | 被content-planner+schedule-manager替代 |
| 素材库规范-飞书多维表格.md | 🟢 | 飞书表结构 |
| 视频生产全链路工具包.md | 🟡 | 工具链已更新(+Zopia)，参考用 |
| 任务督办与业务日报系统方案.md | 🟢 | task-supervisor基础 |

## 其他

| 文件 | 状态 | 说明 |
|------|------|------|
| config/intel-scan-config-v2.json | 🟢 | 7线200+关键词 |
| config/intel-scan-config.json | 🔴 | V1被V2替代 |
| scripts/daily-intel-briefing.py | 🟢 | 情报V2脚本 |
| 新商业布局/ | 🟢 | F/G线新业务 |
| 08-学习笔记/ | 🟢 | 小程序SOP |

---

## 关键提醒

1. **早期规划文档（03-13~03-24）** 很多已过时——那时候还没建Skill，现在以Skill为准
2. **"视频生产双轨方案"有两份都过时了** — 现在是三种模式（品牌/轻量/短剧），看video-producer SKILL.md
3. **"全渠道矩阵运营规划"已过时** — 现在覆盖8个平台，看schedule-manager SKILL.md
4. **"待做表38项"已过时** — 32个Skill已全部建完，看master_roadmap记忆
5. **任何文案/内容规则** — 以B线话术体系定稿和style-manager为准
