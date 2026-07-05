---
name: PaperAlchemy
description: 课件炼金术 — 期末/考前复习 skill。将课件(PDF/DOCX/PPT/教材) + 题库(网站/JSON/MD)整合为自包含 HTML 复习页面。支持"无课件模式"(仅题库+教材名也能用)。三tab布局+错题追踪+模拟考试+KaTeX公式。触发词：期末复习、考试、刷题、备考、考前冲刺、复习笔记、题库。
---

# PaperAlchemy — 课件炼金术

> 课件 + 题库 → 两个自包含 HTML 文件（桌面/手机通用，零依赖）。没课件？仅凭教材名 + 题库也能用。

## 这是什么

输入课件 + 题库 → 输出**两个互补的自包含 HTML 文件**：

| 文件 | 作用 | 适合场景 |
|------|------|----------|
| `课程名-复习笔记.html` | 详细知识点卡片 + 每点 3-5 道例题 + 简答题 + 易错点汇总 + 考前检查清单 | 系统复习、考前速览 |
| `课程名-刷题考试.html` | 交互式刷题（点选作答、即时反馈、解析）、错题追踪、弱项突击、模拟考试 | 大量刷题、查漏补缺 |

两文件数据互通（基于同一套知识点匹配），但功能解耦：笔记文件偏重「看」，刷题文件偏重「练」。

### 核心特性

**复习笔记文件**
- 知识点按讲次组织，侧边栏一键跳转
- 每张卡片含：概念定义、关键要点、记忆钩子、常见错误、考试提示
- 每个知识点配 **3-5 道精选例题**，答案可一键显隐，便于自测
- 简答题专区、常见错误汇总、考前检查清单
- 知识点搜索：输入关键词即时过滤

**刷题考试文件**
- 点击选项即可作答，即时显示正确答案与解析
- 单选 / 多选 / 判断自动判分，填空题自测后手动标记
- 错题自动存入 localStorage，关闭再打开还在
- 「错题重练」一键过滤全部错题
- **弱项仪表盘**：按知识点统计正确率，点击弱项直接突击
- 模拟考试：自选题型和数量，生成试卷后对照答案
- **事件委托 + 懒渲染**：909 道题以紧凑 JSON 存储，交互无 onclick

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
| **OpenCode** | `~/.config/opencode/skills/PaperAlchemy/` | 启动自动扫描 |
| **Claude Code** | `~/.claude/skills/PaperAlchemy/` | 启动自动扫描 |
| **Codex CLI** | `~/.codex/skills/PaperAlchemy/` | 启动自动扫描 |
| **OpenClaw** | `~/.claude/skills/PaperAlchemy/` | 兼容 Claude Code 路径 |
| **Gemini CLI** | `~/.gemini/skills/PaperAlchemy/` | `activate_skill PaperAlchemy` |
| **Copilot CLI** | 项目 `.github/copilot-skills/` | `skill PaperAlchemy` |

**如何安装：**

```bash
# 万能方法：git clone 到对应 agent 的 skills 目录
git clone https://github.com/<your-username>/PaperAlchemy.git ~/.claude/skills/PaperAlchemy/

# 或直接复制 SKILL.md + template/
cp -r path/to/PaperAlchemy ~/.config/opencode/skills/PaperAlchemy/
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

使用 `template/build.py` 的 `build_all()` 函数，一次生成两个文件：

```python
from template.build import build_all

build_all(
    knowledge_points=KNOWLEDGE_POINTS,
    essay_questions=ESSAY_QUESTIONS,
    lecture_titles=LECTURE_TITLES,
    questions_json_path="path/to/questions.json",
    output_dir="path/to/output/",
    course_name="课程名",
    max_sample_questions=5,  # 每个知识点在笔记中展示几道题
)
```

生成的文件：
- `path/to/output/课程名-复习笔记.html`
- `path/to/output/课程名-刷题考试.html`

底层实现：
- `template/shared_utils.py`：题目加载、关键词匹配、紧凑序列化
- `template/notes_template.py`：复习笔记 HTML 生成
- `template/quiz_template.py`：交互刷题 HTML 生成
- 数据以 `window.Q / window.K / window.E / window.L` 注入页面
- CSS + JS 完全内嵌，无需网络（KaTeX 除外）

### 8. 验证

**复习笔记文件**
- [ ] 文件大小合理（~200-350KB，视题目量）
- [ ] 左侧导航可点击跳转
- [ ] 每个知识点展示 3-5 道例题
- [ ] 点击「显示答案」后答案和正确选项高亮
- [ ] 搜索框输入关键词可过滤知识点
- [ ] 考前检查清单勾选状态刷新后保留

**刷题考试文件**
- [ ] 文件大小合理（~100-150KB）
- [ ] 点击选项立即反馈正确/错误
- [ ] 多选题确认后判分
- [ ] 错题自动进入「错题重练」
- [ ] 弱项 TOP 按正确率排序
- [ ] 点击弱项进入「弱项突击」模式
- [ ] 模拟考试可生成试卷并查看答案
- [ ] 手机打开按钮不溢出

## 文件结构

```
skills/PaperAlchemy/
├── SKILL.md                        # 本文件（核心流程）
├── README.md                       # GitHub 展示页
├── template/
│   ├── shared_utils.py             # 题目加载、匹配、紧凑序列化
│   ├── notes_template.py           # 复习笔记 HTML 生成
│   ├── quiz_template.py            # 交互刷题 HTML 生成
│   └── build.py                    # 两文件生成入口
└── references/
    ├── knowledge_card_format.md    # 知识点卡片格式规范
    └── keyword_matching.md         # 关键词匹配策略
```

## 输出产物

```
课程文件夹/
├── 课程名-复习笔记.html    # 系统复习用
└── 课程名-刷题考试.html    # 交互刷题用
```

## v4 vs v3 对比

| | v3 | v4 |
|---|---|---|
| 输出文件 | 1 个 HTML（三 tab） | 2 个 HTML（笔记 + 刷题） |
| 复习笔记 | 三 tab 之一 | 独立文件，更详细的卡片、搜索、检查清单 |
| 刷题交互 | 「显示答案」+ 手动标记会/不会 | 点击选项即时判分 + 解析 |
| 弱项分析 | 无 | 按知识点正确率 TOP 弱项，一键突击 |
| 错题模式 | 手动标记 | 自动记录 + 错题重练 |
| 文件大小 | ~220KB | 笔记 ~230KB + 刷题 ~120KB |

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
3. 填空题无法自动判分，需用户对照答案手动标记
4. 大文件课件（>50MB PDF）解析可能很慢
5. KaTeX 需联网（离线不渲染公式但文字仍可读）
6. 不支持图表/电路图内嵌
7. 依赖 JavaScript（禁用 JS 的浏览器无法使用）

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
