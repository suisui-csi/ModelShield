---
name: 🎯 新增攻击语料
about: 提交一条新的攻击用例（最欢迎的贡献！）
title: "[Corpus] "
labels: corpus
---

## 攻击手法名称

<!-- 例如：伪造行政通知诱导转账 -->

## 所属类别

<!-- 从下列六类中选一个 -->
- [ ] `prompt_injection` 提示词注入
- [ ] `jailbreak` 越狱绕过
- [ ] `sensitive_disclosure` 敏感信息泄露
- [ ] `excessive_agency` 工具滥用/过度代理
- [ ] `harmful_output` 有害内容输出
- [ ] `hallucination` 幻觉与虚构

## 攻击载荷（prompt）

```
（粘贴你准备写进语料库的载荷）
```

## 为什么这条值得加入？

<!-- 说明它的有效性/新颖性，例如：针对中文政务场景、利用了某种新的话术结构 -->

## 建议的判定关键词

<!-- 如果规则可判定，给出响应中会出现的关键词；如果只能靠 LLM 裁判，请说明 -->

## 自检

- [ ] 已运行 `python run_tests.py` 且通过
- [ ] 已确认语料库中无重复用例
- [ ] 载荷中不含真实个人信息或可直接用于犯罪的操作细节
- [ ] 已按 `id / category / name / prompt / violation` 格式填写
