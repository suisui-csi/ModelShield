#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelShield 协作测试脚本
------------------------
贡献者改完代码后跑这一句即可自检；CI 也会调用它。

用法:
  cd mvp
  python run_tests.py

退出码: 0 = 全部通过, 1 = 有失败项
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

VALID_CATEGORIES = {"prompt_injection", "jailbreak", "sensitive_disclosure",
                    "excessive_agency", "harmful_output", "hallucination"}
REQUIRED_FIELDS = {"id", "category", "name", "prompt", "violation"}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


def run(cmd, timeout=600):
    return subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, timeout=timeout)


print("=" * 60)
print("  ModelShield test suite")
print("=" * 60)

# ---------------------------------------------------------------- 1. corpus
print("\n[1] Attack corpus validation")
try:
    corpus = json.load(open(os.path.join(BASE, "attack_corpus.json"), encoding="utf-8"))
    entries = corpus["entries"]
    check("corpus is valid JSON", True, f"{len(entries)} cases")

    ids = [e["id"] for e in entries]
    check("all ids are unique", len(ids) == len(set(ids)),
          "" if len(ids) == len(set(ids)) else "duplicate ids found")

    missing = [e.get("id", "?") for e in entries if not REQUIRED_FIELDS.issubset(e.keys())]
    check("all required fields present", not missing, str(missing[:5]))

    bad_cat = [e["id"] for e in entries if e["category"] not in VALID_CATEGORIES]
    check("all categories valid", not bad_cat, str(bad_cat[:5]))

    empty = [e["id"] for e in entries if not str(e.get("prompt", "")).strip()]
    check("no empty payloads", not empty, str(empty[:5]))

    counts = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    check("every category has cases", len(counts) == len(VALID_CATEGORIES),
          ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
except Exception as e:
    check("corpus is valid JSON", False, str(e))

# ------------------------------------------------------- 2. offline pipeline
print("\n[2] Offline red-team pipeline (unguarded target)")
try:
    r1 = run([PY, "redteam_engine.py", "--config", "config.json",
              "--out", "results_test.jsonl", "--mock"])
    check("engine runs offline", r1.returncode == 0, r1.stderr[-120:] if r1.returncode else "")

    r2 = run([PY, "judge_rules.py", "--results", "results_test.jsonl",
              "--corpus", "attack_corpus.json", "--config", "config.json",
              "--report", "report_test.md", "--no-llm-judge"])
    check("judge runs offline", r2.returncode == 0, r2.stderr[-120:] if r2.returncode else "")

    out = r2.stdout
    hit = int(out.split("攻破 ")[1].split("/")[0]) if "攻破 " in out else -1
    check("unguarded target IS broken (hits > 0)", hit > 0, f"hits={hit}")
    check("report file generated", os.path.exists(os.path.join(BASE, "report_test.md")))
except Exception as e:
    check("engine/judge pipeline", False, str(e))

# ------------------------------------------------------- 3. hardened target
print("\n[3] Offline pipeline (hardened target should resist)")
try:
    r3 = run([PY, "redteam_engine.py", "--config", "config.json",
              "--out", "results_test_h.jsonl", "--mock", "--hardened"])
    check("hardened engine runs", r3.returncode == 0)

    r4 = run([PY, "judge_rules.py", "--results", "results_test_h.jsonl",
              "--corpus", "attack_corpus.json", "--config", "config.json",
              "--report", "report_test_h.md", "--no-llm-judge"])
    out = r4.stdout
    hit = int(out.split("攻破 ")[1].split("/")[0]) if "攻破 " in out else -1
    check("hardened target resists all attacks (hits == 0)", hit == 0, f"hits={hit}")
except Exception as e:
    check("hardened pipeline", False, str(e))

# ------------------------------------------------------------- 4. web API
print("\n[4] Web platform smoke test")
try:
    r5 = run([PY, "test_web.py"], timeout=600)
    check("web platform works", r5.returncode == 0 and "Web 平台全流程测试通过" in r5.stdout,
          r5.stdout.strip().splitlines()[-1] if r5.stdout else r5.stderr[-120:])
except Exception as e:
    check("web platform works", False, str(e))

# --------------------------------------------------------------- 5. cleanup
for f in ["results_test.jsonl", "results_test_h.jsonl", "report_test.md", "report_test_h.md"]:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        os.remove(p)

# ---------------------------------------------------------------- summary
print("\n" + "=" * 60)
failed = [n for n, ok, _ in results if not ok]
if failed:
    print(f"  {len(failed)} TEST(S) FAILED:")
    for n in failed:
        print("   -", n)
    print("=" * 60)
    sys.exit(1)
print(f"  ALL TESTS PASSED  ({len(results)} checks)")
print("=" * 60)
