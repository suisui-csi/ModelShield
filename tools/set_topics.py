#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用专用接口设置仓库 topics"""
import json
import os
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token = open(os.path.join(ROOT, ".token"), encoding="utf-8").read().strip()
REPO = "suisui-csi/ModelShield"

topics = ["ai-security", "llm-security", "red-team", "prompt-injection",
          "ai-agent", "security-testing", "owasp-llm-top10", "chinese",
          "ai-safety", "penetration-testing"]

req = urllib.request.Request(API + f"/repos/{REPO}/topics", method="PUT",
                             data=json.dumps({"names": topics}).encode("utf-8"))
req.add_header("Authorization", "Bearer " + token)
req.add_header("Accept", "application/vnd.github+json")
req.add_header("Content-Type", "application/json")
req.add_header("User-Agent", "ModelShield-Meta")
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
    print("✅ topics 设置成功:", ", ".join(d.get("names", [])))
except Exception as e:
    print("⚠️ 设置失败:", e)

# 复查
req2 = urllib.request.Request(API + f"/repos/{REPO}")
req2.add_header("Authorization", "Bearer " + token)
req2.add_header("Accept", "application/vnd.github+json")
req2.add_header("User-Agent", "ModelShield-Meta")
with urllib.request.urlopen(req2, timeout=60) as r:
    d = json.loads(r.read().decode("utf-8"))
print("复查 topics:", d.get("topics") or "(空)")
print("仓库状态:", d.get("visibility"), "| stars:", d.get("stargazers_count"),
      "| 大小:", d.get("size"), "KB")
