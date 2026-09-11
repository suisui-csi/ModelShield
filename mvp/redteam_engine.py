#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelShield（AI Security Project）· 红队引擎 v0.2
作用：批量把攻击语料发给被测大模型/智能体，收集原始响应作为证据链。

用法:
  真实 API 目标:
    python redteam_engine.py --config config.json --out results.jsonl
  离线模拟靶子（零成本，演示/自测）:
    python redteam_engine.py --config config.json --out results.jsonl --mock
    加固版靶子（对比演示）:
    python redteam_engine.py --config config.json --out results.jsonl --mock --hardened
  其他: --corpus attack_corpus.json --limit 20
"""
import argparse
import json
import sys
import time
from datetime import datetime

from mock_target import MockLLM

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class APITarget:
    """真实大模型目标（OpenAI 兼容 API）"""

    def __init__(self, cfg):
        t = cfg["target"]
        self.client = OpenAI(base_url=t.get("base_url", "https://api.deepseek.com/v1"),
                             api_key=t["api_key"])
        self.model = t.get("model", "deepseek-chat")
        self.system_prompt = t.get("system_prompt", "")

    def chat(self, prompt, timeout=90):
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages,
            temperature=0.7, max_tokens=512, timeout=timeout)
        return resp.choices[0].message.content or ""


def build_target(cfg, use_mock, hardened):
    if use_mock:
        sp = cfg.get("target", {}).get("system_prompt", "")
        return MockLLM(system_prompt=sp, hardened=hardened)
    return APITarget(cfg)


def run_single_attack(target, prompt, timeout=90, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return {"ok": True, "text": target.chat(prompt, timeout=timeout)}
        except Exception as e:
            if isinstance(target, MockLLM):
                return {"ok": False, "error": str(e)[:200]}
            if attempt < max_retries:
                time.sleep(3 * (attempt + 1))
                continue
            return {"ok": False, "error": str(e)[:200]}


def main():
    ap = argparse.ArgumentParser(description="ModelShield 红队引擎")
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--corpus", default="attack_corpus.json")
    ap.add_argument("--out", default="results.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--mock", action="store_true", help="使用本地模拟靶子（离线演示）")
    ap.add_argument("--hardened", action="store_true", help="模拟靶子使用加固模式")
    args = ap.parse_args()

    cfg = load_json(args.config)
    corpus = load_json(args.corpus)["entries"]
    if args.limit > 0:
        corpus = corpus[: args.limit]

    target = build_target(cfg, args.mock, args.hardened)
    if args.mock:
        tgt_desc = "本地模拟靶子（加固版）" if args.hardened else "本地模拟靶子（裸奔版）"
    else:
        tgt_desc = f"{cfg['target'].get('base_url')} / {cfg['target'].get('model')}"

    print(f"[*] 目标: {tgt_desc}")
    print(f"[*] 攻击总数: {len(corpus)}\n")

    total_ok, total_fail = 0, 0
    with open(args.out, "w", encoding="utf-8") as out:
        for i, entry in enumerate(corpus, 1):
            t0 = time.time()
            r = run_single_attack(target, entry["prompt"])
            cost = time.time() - t0

            record = {
                "id": entry["id"], "category": entry["category"],
                "name": entry["name"], "prompt": entry["prompt"],
                "violation": entry["violation"],
                "response": r.get("text", ""), "ok": r["ok"],
                "error": r.get("error", ""), "elapsed_s": round(cost, 2),
                "ts": datetime.now().isoformat(timespec="seconds"),
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

            if r["ok"]:
                total_ok += 1
                preview = r["text"].replace("\n", " ")[:44]
                print(f"  [{i:>2}/{len(corpus)}] {entry['name']:<16} → {preview}")
            else:
                total_fail += 1
                print(f"  [{i:>2}/{len(corpus)}] {entry['name']:<16} → ✗ {r['error'][:40]}")

            if not args.mock:
                time.sleep(args.sleep)

    print(f"\n[+] 完成: 成功 {total_ok} / 失败 {total_fail} | 结果: {args.out}")
    print("[*] 下一步: python judge_rules.py --results results.jsonl --corpus attack_corpus.json --config config.json --report report.md")


if __name__ == "__main__":
    main()
