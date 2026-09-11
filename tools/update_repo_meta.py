#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新 GitHub 仓库元信息（描述 + 标签）"""
import json
import os
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, ".token")
REPO = "suisui-csi/ModelShield"

token = open(TOKEN_FILE, encoding="utf-8").read().strip()

payload = {
    "description": "模盾 ModelShield · AI大模型与智能体安全体检平台 | 自动化红队评测 + 中文攻击语料库 + 白话体检报告",
    "homepage": "",
    "topics": ["ai-security", "llm-security", "red-team", "prompt-injection",
               "ai-agent", "security-testing", "owasp-llm-top10", "chinese"],
}

req = urllib.request.Request(API + f"/repos/{REPO}", method="PATCH",
                             data=json.dumps(payload).encode("utf-8"))
req.add_header("Authorization", "Bearer " + token)
req.add_header("Accept", "application/vnd.github+json")
req.add_header("Content-Type", "application/json")
req.add_header("User-Agent", "ModelShield-Meta")
with urllib.request.urlopen(req, timeout=60) as r:
    d = json.loads(r.read().decode("utf-8"))
print("✅ 仓库信息已更新")
print("   描述:", d.get("description"))
print("   标签:", ", ".join(d.get("topics", [])))
print("   地址:", d.get("html_url"))
