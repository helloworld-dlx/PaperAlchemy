---
name: PaperAlchemy
description: 课件炼金术 — 期末/考前复习 skill。将课件(PDF/DOCX/PPT/教材) + 题库(网站/JSON/MD)整合为自包含 HTML 复习页面。支持"无课件模式"(仅题库+教材名也能用)。三tab布局+错题追踪+模拟考试+KaTeX公式。触发词：期末复习、考试、刷题、备考、考前冲刺、复习笔记、题库。
---

# PaperAlchemy — 课件炼金术

> 课件 + 题库 → HTML 复习页面。没课件？仅凭教材名 + 题库也能用。

## 这是什么

输入课件 + 题库 → 输出一个**自包含 HTML 文件**（桌面/手机通用，零依赖）。

### 三 Tab 布局

| Tab | 功能 |
|-----|------|
| 复习脉络 | 知识点卡片（概念/要点/钩子/易错点）+ 每个知识点 Top-6 题目 +「去刷题」按钮 |
| 刷题考试 | 动态渲染全部题目，可按知识点/题型筛选，「只看错题」模式，错题自动存 localStorage |
| 模拟考试 | 随机抽题，可选题型和数量，「生成试卷」→「查看答案」→ 回刷题 tab 标记错题 |

### 核心特性

- 知识点按讲次组织，侧边栏一键跳转
- 每道题「我会了 / 我不会」标记，存 localStorage，关闭再打开还在
- **标记可撤销**：再点一次取消标记
- 「只看错题」模式：一键过滤未掌握的题目
- **进度条**：显示已标记题目/总题数的百分比（真实复习进度，不依赖滚动）
- 简答题专区：AI 根据课件预测 15-25 道高频简答题
- **事件委托**：909 道题的 onclick 全消失（127KB → 0），体积从 986KB 压到 ~220KB
- **懒渲染**：题目以紧凑 JSON 存储，按需动态生成 DOM
- **页面标题可定制**：`COURSE_NAME` 配置项控制标题和顶栏显示的课程名

## 什么时候用

- 用户提到"期末复习""考试""备考""刷题""题库""考前冲刺"
- 用户有课件资料（PPT/PDF/DOCX/讲义）需要整理
- 用户有题库（网页/JSON/Markdown）需要刷题
- 用户希望生成一个能直接看的复习页面

**不适合：**
- 长期系统学习（>30天）— 用 ko-lesson
- 既没有课件也没有题库 — 两条路径都走不了
- 只需要问几个问题 — 直接问 AI 就行
- 需要精美打印排版 — 用 NovaForge

## 适用范围

| 课程类型 | 推荐 | 说明 |
|----------|------|------|
| 文科/经管/思政（记忆为主） | ✅ | 完美匹配 |
| 理工科（有公式） | ✅ | `USE_KATEX=True` 启用公式渲染 |
| 理工科（有图表/电路图） | ⚠️ | 图表需额外处理 |
| 纯实践/实验课 | ❌ | 不适合 |

## 跨 Agent 兼容性

同一份 `SKILL.md` + `template/page_template.py`，所有 agent 通用：

| Agent | 安装路径 | 加载方式 |
|-------|---------|---------|
| **OpenCode** | `~/.config/opencode/skills/exam-review/` | 启动自动扫描 |
| **Claude Code** | `~/.claude/skills/exam-review/` | 启动自动扫描 |
| **Codex CLI** | `~/.codex/skills/exam-review/` | 启动自动扫描 |
| **OpenClaw** | `~/.claude/skills/exam-review/` | 兼容 Claude Code 路径 |
| **Gemini CLI** | `~/.gemini/skills/exam-review/` | `activate_skill exam-review` |
| **Copilot CLI** | 项目 `.github/copilot-skills/` | `skill exam-review` |

**如何安装：**

```bash
# 万能方法：git clone 到对应 agent 的 skills 目录
git clone https://github.com/<your-username>/exam-review.git ~/.claude/skills/exam-review/

# 或直接复制 SKILL.md + template/
cp -r path/to/exam-review ~/.config/opencode/skills/exam-review/
```

## 完整工作流程

### 1. 收集信息

向用户确认：
1. **课件资料路径** — PDF/DOCX/PPT/教材图片 所在的文件夹（可选）
2. **题库来源** — 网址（GitHub Pages 刷题网站）、本地文件（JSON/MD）
3. **教材名/版本**（可选）— 如果无课件，至少要知道教材名
4. **考试日期**（可选）
5. **是否启用 KaTeX**（理工科课程）

**重要判断：用户有没有课件资料？**

#### 有课件模式（默认）
用户有 PDF/DOCX/PPT 文件 → 走正常课件解析流程。

#### 无课件模式
用户只有题库 + 教材名（如"创新创业基础 第X版，杨琛琛"），没有电子版课件。

进入无课件模式时：

1. **分析题库反推知识点**：扫描全部题目的高频词和主题聚类。哪些概念反复出现？哪些题型对应哪些章节？题库本身已经暴露了考试重点。

2. **从教材名搜索补充信息**：用教材名去网上搜索目录/大纲/简介（如豆瓣、出版社官网、电商页面）。如果搜到了目次，逐章对应到知识聚类。如果搜到了书的简介或部分内容，提取关键概念。

3. **AI 合成知识点卡片**：结合题库分析和网络搜索结果，为每个知识聚类生成知识点卡片。**必须标注**"定义由 AI 根据题库推断，建议核对教材"。

4. **记忆钩子和易错点从题目中来**：钩子从高频考点中归纳；易错点从题目错误选项中分析出常见掉坑模式。

5. **后续流程不变**：知识点→关键词→匹配题目→生成 HTML。

**无课件模式的产出质量取决于题库覆盖面。** 如果题库覆盖了考试大部分知识点，生成的卡片基本够用；如果题库不全，会漏知识点。

### 2. 解析课件

- PDF：PyPDF2/pypdf 逐页提取文本
- DOCX：python-docx 提取段落
- PPT：python-pptx 提取文本
- **不能一股脑合并后给 AI 总结**— 要逐讲细读

### 3. 提取题库

- 网站内嵌数据（`const ALL_QUESTIONS = [...]`）：用正则截取 + Node.js `eval()` 解析
- 前端渲染页面：查看 Network 请求找数据接口
- 本地 JSON/MD：直接读取

### 4. 逐讲提取知识点

每讲提取 5-8 个知识点，每个包含：
```
title: 知识点名称
definition: 概念定义（1-3句）
key_points: 关键要点（3-5条）
memory_hook: 记忆钩子/口诀
common_mistakes: 常见错误（2-3条）
keywords: 关键词（5-15个，用于题目匹配）
```

### 5. 题目匹配

- 每知识点 5-15 个关键词
- 题目文本 + 选项加权匹配：完整关键词 +3，部分匹配 +1
- 未匹配题目归入最近知识点
- 匹配后统计，题目过多（>100）/过少（<3）的知识点需要调整

### 6. 生成简答题

AI 根据课件预测 15-25 道高频简答题，覆盖每讲至少 2 道。

### 7. 生成 HTML

编写或复用 `page_template.py` 构建脚本：
- 题目序列化为紧凑 JSON（`[id, typeNum, q, [opts], ans]`）
- 知识点注入为 JS 对象数组（含匹配题目索引）
- CSS + JS 内嵌在 `<style>` 和 `<script>` 中
- 三类数据 `window.Q / window.K / window.E / window.L` 注入 HTML

**脚本关键参数：**
```python
tpl.COURSE_NAME = "课程名称 · 期末复习笔记"  # 页面标题
tpl.DEFAULT_SHOW = 6    # 每个知识点默认展示题目数
tpl.USE_KATEX = False   # 理工科设 True
tpl.OUTPUT_PATH = "path/to/课程名-期末复习笔记.html"  # 输出路径（建议含课程名）
```

### 8. 验证

- [ ] 文件大小合理（~200-350KB，视题目量）
- [ ] 浏览器打开三个 tab 都正常渲染
- [ ] 手机打开按钮不溢出
- [ ] localStorage 错题标记关闭再打开还在
- [ ] 「我会了」点两次取消标记
- [ ] 「只看错题」只显示标记为不会的题

## 文件结构

```
skills/exam-review/
├── SKILL.md                        # 本文件（核心流程）
├── README.md                       # GitHub 展示页
├── template/
│   └── page_template.py            # HTML 生成模板（CSS+JS+Python）
└── references/
    ├── knowledge_card_format.md    # 知识点卡片格式规范
    └── keyword_matching.md         # 关键词匹配策略
```

## 输出产物

```
课程文件夹/
└── 期末复习笔记.html    # 自包含 HTML，浏览器直接打开
```

## v3 vs v2 对比

| | v2 | v3 |
|---|---|---|
| 文件大小 | ~986KB | ~220KB |
| 题目渲染 | HTML 预渲染全部 | JSON 存储 + 懒渲染 |
| 事件绑定 | onClick(每道题2个) | 事件委托(全局1个) |
| 布局 | 单视图滚动 | 三 tab（脉络/刷题/模拟） |
| 标记撤销 | 不支持 | 再点一次取消 |
| 筛选 | 无 | 按知识点/题型/只看错题 |

## 已知局限

1. 简答题预测靠 AI 推断，需用户对照真实考试范围调整
2. 关键词匹配可能有少量错配
3. 大文件课件（>50MB PDF）解析可能很慢
4. KaTeX 需联网（离线不渲染公式但文字仍可读）
5. 不支持图表/电路图内嵌
6. 依赖 JavaScript（禁用 JS 的浏览器无法使用）

## 对比同类工具

| | PaperAlchemy | ko-lesson | NovaForge | zero-to-pass |
|---|---|---|---|---|
| 题库支持 | ✅ 爬网站/读JSON | ❌ 自己出题 | ❌ | ✅ 试卷文件 |
| 学习闭环 | 错题追踪+只看错题 | 反馈→巩固卷→循环 | ❌ | ❌ |
| 输出 | 自包含HTML | Obsidian多个md | LaTeX/PDF | Markdown |
| 移动端 | ✅ 适配 | 需Obsidian app | PDF可看 | 勉强 |
| 公式支持 | ✅ KaTeX | ❌ | ✅ LaTeX强 | ❌ |
| 文件大小 | ~220KB | 多个小文件 | PDF适中 | 按需 |
| 安装 | 任何agent | 仅Codex | Claude Code | 多个agent |
