# 模盾 ModelShield 🛡

> 让每一个 AI 应用上线前先过"安检"
> **AI 安全体检平台** —— 自动化红队测试你的大模型 / AI 智能体，30 秒出一份能看懂的安全体检报告。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## ✨ 它能做什么

- **60+ 中文攻击语料**：提示词注入、越狱、敏感信息套取、工具滥用、有害内容、幻觉虚构（对齐 OWASP LLM Top 10）
- **一键红队**：批量把攻击发给你的 AI 应用，收集原始响应（证据链可复核）
- **安全体检报告**：综合评分 + 分类命中率 + 命中明细 + 修复建议（自动生成 Markdown）
- **离线模拟靶子**：零成本、断网可用，演示/自测两相宜；含"裸奔版 vs 加固版"对比
- **Web 平台**：浏览器点几下就能完成整个体检流程

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install openai flask

# 2. 离线演示（零成本，不需要任何 API Key）
cd mvp
python redteam_engine.py --config config.json --out results.jsonl --mock
python judge_rules.py --results results.jsonl --corpus attack_corpus.json --config config.json --report report.md --no-llm-judge

# 3. 打开报告
#    查看生成的 report.md —— 这就是第一份《AI 安全体检报告》

# 4. 启动 Web 平台（可选）
python app.py
# 浏览器打开 http://127.0.0.1:5000
```

### 对真实大模型测试

1. 注册 [DeepSeek](https://platform.deepseek.com)（或其他 OpenAI 兼容服务）并获取 API Key
2. 编辑 `mvp/config.json`：填入 `api_key`，按需修改 `model` 与 `system_prompt`
3. 运行（不带 `--mock`）：
```bash
python redteam_engine.py --config config.json --out results.jsonl
python judge_rules.py --results results.jsonl --corpus attack_corpus.json --config config.json --report report.md
```

## 📁 目录结构

```
.
├── README.md
├── LICENSE
└── mvp/
    ├── attack_corpus.json     # 攻击语料库（72 条，6 大类）
    ├── redteam_engine.py      # 红队引擎（API 目标 / 本地模拟靶子）
    ├── judge_rules.py         # 判定引擎 + 体检报告生成
    ├── mock_target.py         # 离线模拟靶子（裸奔版 / 加固版）
    ├── app.py                 # Web 平台（Flask）
    ├── config.json            # 目标与裁判配置
    └── demo_target_prompt.md  # 演示靶子：银行客服 AI 提示词对比
```

## 🧪 技术原理

```
攻击语料库 ──▶ 红队引擎 ──▶ 被测 AI（API / 模拟靶子）
                  │
                  ▼
            原始响应(证据链)
                  │
                  ▼
         规则判定 + LLM裁判 ──▶ 评分 ──▶ 体检报告(Markdown/Web)
```

- **规则判定**：每类攻击配证据关键词库，命中即违规（可解释、零成本）
- **LLM 裁判**（可选）：对规则兜不住的情形（幻觉、语义级违规）做二次判定
- **加权评分**：按 OWASP LLM Top 10 风险严重度加权，输出 0-100 安全分

## 🗺 Roadmap

- [x] v0.1 攻击语料库 + 红队引擎 + 规则判定 + 报告
- [x] v0.2 离线模拟靶子 + Web 平台 + 语料扩充
- [ ] v0.3 多轮对话攻击（Multi-turn Jailbreak）
- [ ] v0.4 AI Agent 工具调用靶场（邮件助手/客服助手）
- [ ] v0.5 攻击剧本社区（众包贡献 + 排行榜）
- [ ] v0.6 CI 集成（上线前自动体检，不达标阻断发布）

## 🤝 贡献

欢迎贡献攻击语料、判定规则、新靶场！

1. Fork 本仓库
2. 新建分支（`feat/你的点子`）
3. 提交代码
4. 发起 Pull Request

**贡献攻击语料**：直接向 `mvp/attack_corpus.json` 添加条目即可（保持 `id/category/name/violation/prompt` 格式）。

## ⚠️ 合规与免责声明

本项目仅用于**授权测试、安全研究、教学演示**。
- 只可对你拥有或被明确授权的 AI 应用发起测试
- 攻击语料中的请求示例仅用于防御评估，请勿用于非法用途
- 使用本项目产生的任何行为与后果，由使用者自行承担

## 📄 License

[MIT](LICENSE) © 2026 ModelShield Team
