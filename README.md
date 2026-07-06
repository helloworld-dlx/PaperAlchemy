# PaperAlchemy — 课件炼金术

> 课件 + 题库 → HTML 复习页面。没课件？仅凭教材名 + 题库也能用。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Platform: All Agents](https://img.shields.io/badge/agents-OpenCode%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20Gemini%20CLI%20%7C%20Copilot-success)]()
[![Output: HTML](https://img.shields.io/badge/output-self--contained%20HTML-orange)]()

## 功能预览

一次生成两个互补的 HTML 文件：

| 课程名-复习笔记.html | 课程名-刷题考试.html |
|---|---|
| 知识点卡片 + 记忆钩子 + 易错点 | 点击选项即时作答、即时反馈 |
| 每知识点 3-5 道精选例题 | 单选/多选/判断自动判分 |
| 简答题专区 + 考前检查清单 | 错题自动记录，错题重练 |
| 知识点搜索 | 弱项 TOP 排行榜，一键突击 |
| | 模拟考试 + 自定义题型数量 |

![复习笔记](https://raw.githubusercontent.com/helloworld-dlx/PaperAlchemy/main/assets/review.png)

![刷题考试](https://raw.githubusercontent.com/helloworld-dlx/PaperAlchemy/main/assets/quiz.png)

### 一句话说清

把老师给的 PPT 和你找到的题库网站整合成两个文件：一个用来系统看笔记，一个用来交互刷题。**错题记录存在浏览器本地**，关了再打开还在。

## 安装

### 方式 1：克隆到 skills 目录（推荐）

```bash
# Claude Code / OpenClaw
git clone https://github.com/helloworld-dlx/PaperAlchemy.git ~/.claude/skills/PaperAlchemy/

# OpenCode
git clone https://github.com/helloworld-dlx/PaperAlchemy.git ~/.config/opencode/skills/PaperAlchemy/

# Codex
git clone https://github.com/helloworld-dlx/PaperAlchemy.git ~/.codex/skills/PaperAlchemy/
```

### 方式 2：一键安装

```bash
# 使用 skills CLI（如果已安装）
npx skills add user/PaperAlchemy
```

### 支持的所有 Agent

| Agent | 安装路径 |
|-------|---------|
| OpenCode | `~/.config/opencode/skills/PaperAlchemy/` |
| Claude Code | `~/.claude/skills/PaperAlchemy/` |
| Codex CLI | `~/.codex/skills/PaperAlchemy/` |
| OpenClaw | `~/.claude/skills/PaperAlchemy/` |
| Gemini CLI | `~/.gemini/skills/PaperAlchemy/` |
| Copilot CLI | 项目 `.github/copilot-skills/` |

## 快速开始

安装后在 Agent 中触发：

```
帮我期末复习，课件在 D:\我的课件\，题库在 https://xxx.github.io/quiz/
```

Agent 会自动：
1. 解析课件（PDF/DOCX/PPT）
2. 爬取题库
3. 提取知识点
4. 匹配题目到知识点
5. 生成两个文件：`课程名-复习笔记.html` + `课程名-刷题考试.html`

## 配置

在 `template/build.py` 调用时传入：

```python
build_all(
    ...,
    max_sample_questions=5,  # 笔记中每个知识点展示几道题
)
```

如需启用 KaTeX，在 `notes_template.py` / `quiz_template.py` 顶部设置 `USE_KATEX = True`。

## 适用场景

| ✅ 适合 | ❌ 不适合 |
|---------|----------|
| 考前 3-14 天冲刺复习 | 30 天以上长期学习（用 ko-lesson） |
| 有题库需要大量刷题 | 需要打印精美笔记（用 NovaForge） |
| 手机/电脑都能复习 | 纯实验/实践课 |
| 文科/经管/思政/理工科 | |

## 与同类工具对比

| | PaperAlchemy | ko-lesson | NovaForge | zero-to-pass |
|---|---|---|---|---|
| 题库支持 | ✅ 真实题库匹配 | ❌ 自己出题 | ❌ | ✅ 试卷文件 |
| 错题追踪 | ✅ localStorage 持久化 | 学习状态文件 | ❌ | ❌ |
| 输出形式 | 自包含 HTML | Obsidian md | LaTeX/PDF | Markdown |
| 移动端 | ✅ | 需 Obsidian app | PDF 可看 | 勉强 |
| 体积 | ~220KB | 多个文件 | PDF 适中 | 按需 |

## 文件结构

```
.
├── SKILL.md                 # Skill 定义（Agent 加载入口）
├── README.md                # 本文件
├── template/
│   ├── shared_utils.py      # 题目加载、匹配、紧凑序列化
│   ├── notes_template.py    # 复习笔记 HTML 生成
│   ├── quiz_template.py     # 交互刷题 HTML 生成
│   └── build.py             # 两文件生成入口
└── references/
    ├── knowledge_card_format.md
    └── keyword_matching.md
```

## FAQ

**Q: 生成的 HTML 能在手机上打开吗？**

A: 可以。微信发给自己直接打开，或用文件管理器 + 浏览器。

**Q: 错题记录存储在哪里？**

A: 浏览器的 localStorage。不清除浏览器数据就不会丢。

**Q: 理工科公式怎么办？**

A: 模板设置 `USE_KATEX=True`，自动支持 `$...$` 和 `$$...$$` 公式渲染。

**Q: 生成的两个文件是不是漏了题目？**

A: 没有。全部题目以紧凑 JSON 存储在 JS 变量里，打开页面后动态渲染。笔记文件只展示每个知识点的 3-5 道例题，完整题库在刷题文件中。

## 贡献

欢迎提 Issue 和 PR。适合的贡献方向：

- 新功能建议（如 PDF 导出、计时考试）
- HTML 样式和交互优化
- 其他 Agent 的适配测试
- 文档改进

## License

MIT
