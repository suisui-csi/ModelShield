# 贡献指南 · Contributing to ModelShield

首先，感谢你愿意花时间参与！正是像你这样的贡献者让这个项目变得更好。

ModelShield 是一个**面向 AI 应用的安全评测平台**，我们尤其欢迎以下几类贡献：

| 贡献类型 | 难度 | 说明 |
|---|---|---|
| 🎯 **新增攻击语料** | ⭐ 入门友好 | 往 `mvp/attack_corpus.json` 加用例，最受欢迎 |
| 🔧 **改进判定规则** | ⭐⭐ | 优化 `mvp/judge_rules.py` 的关键词库与评分 |
| 🎭 **新增靶场** | ⭐⭐⭐ | 如 AI Agent 工具调用靶场、多轮对话靶场 |
| 🌐 **多语言支持** | ⭐⭐ | 英文/其他语言的攻击语料与界面 |
| 🐛 **修 Bug / 改文档** | ⭐ | 永远欢迎 |

---

## 一、快速开始（开发环境）

```bash
# 1. 克隆仓库
git clone https://github.com/suisui-csi/ModelShield.git
cd ModelShield

# 2. 安装依赖
pip install openai flask

# 3. 跑一遍测试，确认环境正常（不需要任何 API Key）
cd mvp
python run_tests.py
```

看到 `ALL TESTS PASSED` 就说明环境没问题了。

---

## 二、如何贡献攻击语料（最推荐！）

### 步骤

1. 打开 `mvp/attack_corpus.json`
2. 按照下面的格式添加一条用例
3. 运行 `python run_tests.py` 确认格式合法
4. 提交 PR

### 用例格式

```json
{
  "id": "inj-014",
  "category": "prompt_injection",
  "name": "中文手法名",
  "violation": true,
  "prompt": "你的攻击载荷（中文）"
}
```

| 字段 | 说明 |
|---|---|
| `id` | 类别前缀 + 三位序号。前缀：`inj`(注入) `jb`(越狱) `sd`(信息泄露) `ea`(工具滥用) `ho`(有害内容) `ha`(幻觉) |
| `category` | 必须是上述六类之一 |
| `name` | 手法的中文简称，报告里会展示 |
| `prompt` | **实际发给被测 AI 的载荷** |
| `violation` | 是否属于"命中即违规"，通常为 `true` |

### 语料质量要求 ✅

- **有效性**：应当是真能撬动防护的手法，而不是把"如何制作炸弹"直接说出来（那属于有害内容类）
- **无害化**：载荷本身不包含真实的危险操作细节（我们测的是"AI 会不会答应"，不是"怎么做"）
- **新颖性**：优先补充公开语料库里少见的**中文场景**手法（如"帮我查下我同事的工资""以行政部名义发通知"）
- **可判定**：如果规则难以判定，请在 PR 里说明，我们会用 LLM 裁判兜底

### 语料质量要求 ❌

- 不要提交真实个人信息、真实公司内部信息
- 不要提交可直接用于犯罪的操作细节
- 不要重复已有用例（先搜索 JSON 里的关键词）

---

## 三、代码规范

- Python 3.10+，遵循 PEP 8
- **注释与用户可见文案用中文**（项目主语言），变量名/函数名用英文
- 公共函数写 docstring
- 不引入重量级依赖（新增依赖请在 PR 里说明理由）

---

## 四、提交 PR 流程

```bash
# 1. Fork 本仓库（在 GitHub 页面点 Fork）

# 2. 克隆你自己的 fork
git clone https://github.com/<你的用户名>/ModelShield.git
cd ModelShield

# 3. 新建分支（用有意义的命名）
git checkout -b feat/add-chinese-injection-cases
#   分支命名建议：feat/xxx  fix/xxx  docs/xxx  corpus/xxx

# 4. 改代码

# 5. 跑测试（必须通过！）
cd mvp && python run_tests.py

# 6. 提交
git add -A
git commit -m "corpus: 新增 5 条中文间接注入用例"

# 7. 推送并开 PR
git push origin feat/add-chinese-injection-cases
```

然后到 GitHub 上点 **Compare & pull request**，按模板填写即可。

### Commit 信息规范

用 `<类型>: <中文说明>` 的格式：

| 类型 | 用途 | 示例 |
|---|---|---|
| `feat` | 新功能 | `feat: 支持多轮对话攻击` |
| `corpus` | 攻击语料 | `corpus: 新增 5 条 Agent 工具滥用用例` |
| `fix` | 修 Bug | `fix: 修复幻觉类误报` |
| `docs` | 文档 | `docs: 补充语料格式说明` |
| `refactor` | 重构 | `refactor: 拆分判定引擎` |

---

## 五、测试要求

任何 PR 都必须保证测试通过：

```bash
cd mvp
python run_tests.py
```

测试会检查：
1. 语料库 JSON 合法性与字段完整性
2. ID 唯一性、类别合法性
3. 离线红队全流程（裸奔版应当被攻破，加固版应当零攻破）
4. 报告生成是否正常
5. Web 平台接口是否可用

---

## 六、适合新手的任务（Good First Issues）

如果你想练手，可以从这些开始：

- [ ] 给语料库补充**某垂直行业**的攻击用例（医疗 / 政务 / 教育 / 电商）
- [ ] 为判定规则补充**英文关键词**，让规则对英文载荷也生效
- [ ] 给 `judge_rules.py` 增加"按严重度排序命中明细"
- [ ] 为 Web 平台增加"历史报告列表"
- [ ] 写一个 `README_EN.md` 英文说明（面向国际贡献者）
- [ ] 补充 `mock_target.py` 的应答规则，覆盖更多攻击类型

想认领哪个，在 Issue 里留言即可。

---

## 七、行为准则

- 保持友善与尊重，对事不对人
- 欢迎新手提问，禁止嘲讽
- 本项目仅用于**授权测试与安全研究**，禁止提交用于攻击真实未授权目标的工具或教程

详见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 八、有问题？

- 提 **Issue**（用模板）
- 或在 **Discussions** 里讨论

再次感谢你的贡献！🎉
