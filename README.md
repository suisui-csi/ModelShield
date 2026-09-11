# ModelShield 🛡

> **AI Security Project** · 面向大模型与 AI 智能体的安全体检平台
> 让每一个 AI 应用上线前先过"安检"

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Corpus](https://img.shields.io/badge/攻击语料-71条-orange)](mvp/attack_corpus.json)
[![OWASP](https://img.shields.io/badge/对齐-OWASP%20LLM%20Top%2010-purple)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

ModelShield 是一个开源的 **AI 安全评测工具**：自动对你的大模型应用或 AI 智能体做红队测试，
然后生成一份**能看懂的安全体检报告**——哪里被攻破、怎么被攻破、怎么修。

内置 71 条中文攻击语料、离线模拟靶子和一个轻量 Web 平台。

---

## 📊 实测效果（可复现）

同一批 **71 条攻击**，分别打向"无防护"和"加了护栏"两个 AI 客服：

| 被测目标 | 攻破数 | 安全评分 | 风险等级 |
|---|---|---|---|
| ❌ 裸奔版 AI 客服 | **43 / 71** | **36 / 100** | 🔴 高风险 |
| ✅ 加固版 AI 客服 | **0 / 71** | **100 / 100** | 🟢 低风险 |

裸奔版分类命中率：

| 攻击类别 | 命中率 |
|---|---|
| 提示词注入 / Prompt Injection | 92% |
| 越狱绕过 / Jailbreak | 83% |
| 敏感信息泄露 / Sensitive Disclosure | 75% |
| 有害内容输出 / Harmful Output | 55% |
| 工具滥用 / Excessive Agency | 50% |

> 用下方「快速开始」的离线模式即可复现，**不需要任何 API Key**。

---

## ✨ 功能特性

- **71 条攻击语料**：提示词注入、越狱、敏感信息泄露、工具滥用、有害内容、幻觉虚构，对齐 OWASP LLM Top 10
- **一键红队**：批量发起攻击并留存**可复核的原始响应证据链**
- **体检报告**：加权评分 + 分类命中率 + 命中明细 + 修复建议（自动生成 Markdown）
- **离线模拟靶子**：零成本、断网可用，含"裸奔版 vs 加固版"对比
- **Web 平台**：浏览器里完成整个评测流程

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install openai flask

# 2. 离线演示（零成本，不需要任何 API Key）
cd mvp
python redteam_engine.py --config config.json --out results.jsonl --mock
python judge_rules.py --results results.jsonl --corpus attack_corpus.json \
                      --config config.json --report report.md --no-llm-judge

# 3. 查看生成的 report.md —— 这就是第一份《AI 安全体检报告》

# 4. 启动 Web 平台（可选）
python app.py          # http://127.0.0.1:5000
```

### 对真实大模型测试

1. 注册任意 OpenAI 兼容服务（DeepSeek / 通义 / 智谱…）获取 API Key
2. 复制 `mvp/config.example.json` 为 `mvp/config.json`，填入 `api_key`
3. 去掉 `--mock` 运行：

```bash
python redteam_engine.py --config config.json --out results.jsonl
python judge_rules.py --results results.jsonl --corpus attack_corpus.json \
                      --config config.json --report report.md
```

---

## 📁 仓库结构

```
.
├── README.md
├── LICENSE
├── docs/
│   └── AI-Security-Project.md      # 项目设计文档（架构 / 能力 / 使用）
├── mvp/
│   ├── attack_corpus.json          # 71 条攻击语料
│   ├── redteam_engine.py           # 红队引擎（API 目标 / 离线靶子）
│   ├── judge_rules.py              # 判定引擎 + 体检报告生成
│   ├── mock_target.py              # 离线模拟靶子（裸奔版 / 加固版）
│   ├── app.py                      # Web 平台（Flask）
│   ├── config.example.json         # 目标与裁判配置模板
│   ├── demo_target_prompt.md       # 演示靶子：银行客服提示词对比
│   └── test_web.py                 # Web 接口冒烟测试
└── tools/
    ├── push_via_api.py             # 通过 GitHub API 推送（绕过被墙的 git 通道）
    ├── verify_push.py              # 推送后验证与密钥扫描
    ├── update_repo_meta.py         # 设置仓库描述
    └── set_topics.py               # 设置仓库标签
```

---

## 🧪 技术原理

```
attack_corpus.json ──▶ 红队引擎 ──▶ 被测 AI（API / 模拟靶子）
                          │
                          ▼
                    原始响应（证据链）
                          │
                          ▼
            规则判定 + LLM 裁判 ──▶ 评分 ──▶ 体检报告（MD / Web）
```

- **规则判定**：每类攻击配证据关键词库，命中即违规；完全可解释、零成本
- **LLM 裁判**（可选）：对规则兜不住的情形（幻觉、语义级违规）做二次判定
- **加权评分**：按 OWASP LLM Top 10 的风险严重度加权，输出 0–100 安全分

---

## 🗺 Roadmap

- [x] v0.1 攻击语料库 + 红队引擎 + 规则判定 + 报告
- [x] v0.2 离线模拟靶子 + Web 平台 + 语料扩充至 71 条
- [ ] v0.3 多轮对话攻击（Multi-turn Jailbreak）
- [ ] v0.4 AI Agent 工具调用靶场（邮件助手 / 客服助手）
- [ ] v0.5 攻击剧本社区（众包贡献 + 排行榜）
- [ ] v0.6 CI 集成（上线前自动体检，不达标阻断发布）

---

## 🤝 贡献

欢迎贡献攻击语料、判定规则和新的靶场：

1. Fork 本仓库
2. 新建分支（`feat/你的点子`）
3. 提交代码
4. 发起 Pull Request

**贡献攻击语料**：直接向 `mvp/attack_corpus.json` 添加条目，保持
`id / category / name / prompt / violation` 格式即可。

---

## ⚠️ 合规与免责声明

本项目仅用于**授权测试、安全研究、教学演示**。

- 只可对你拥有或被明确授权的 AI 应用发起测试
- 攻击语料中的请求示例仅用于防御评估，请勿用于非法用途
- 使用本项目产生的任何行为与后果，由使用者自行承担

---

## 📄 License

[MIT](LICENSE) © 2026 ModelShield Team
