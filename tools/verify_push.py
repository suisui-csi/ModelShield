#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推送后验证：文件完整性 + 敏感信息检查"""
import base64
import json
import os
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, ".token")
REPO = "suisui-csi/ModelShield"
DECOY = "sk-" + "在此填入"   # 占位符，非真实密钥
GH_PREFIX = "gh" + "p_"      # 拆开书写，避免被 GitHub 密钥扫描误判
PAT_MIN_LEN = 30

token = open(TOKEN_FILE, encoding="utf-8").read().strip()


def api(path):
    req = urllib.request.Request(API + path)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "ModelShield-Verify")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


print("=" * 56)
print("  推送后验证报告")
print("=" * 56)

tree = api(f"/repos/{REPO}/git/trees/main?recursive=1")
blobs = [t for t in tree["tree"] if t["type"] == "blob"]
remote = sorted(t["path"] for t in blobs)

print(f"\n【1】远程文件清单（{len(remote)} 个）")
for p in remote:
    print("   ✓", p)

print("\n【2】敏感文件检查")
danger = [p for p in remote if p.endswith(("config.json", ".token", ".env"))
          and "example" not in p]
print("   🔴 危险！发现疑似密钥文件: " + str(danger) if danger
      else "   ✅ 未发现 config.json / .token / .env 等敏感文件")

print("\n【3】文件内容密钥扫描（<200KB 的文件）")
suspicious = []
for t in blobs:
    if t.get("size", 0) > 200000:
        continue
    blob = api(f"/repos/{REPO}/git/blobs/{t['sha']}")
    if blob.get("encoding") != "base64":
        continue
    content = base64.b64decode(blob["content"]).decode("utf-8", "ignore")
    for line in content.splitlines():
        s = line.strip()
        if "sk-" in s and DECOY not in s and "api_key" in line:
            suspicious.append((t["path"], s[:50]))
        if GH_PREFIX in s and len(s) > PAT_MIN_LEN:
            suspicious.append((t["path"], s[:50]))

if suspicious:
    print("   🔴 发现可疑密钥行:")
    for p, s in suspicious:
        print(f"      {p}: {s}…")
else:
    print("   ✅ 未发现真实密钥（config.example.json 仅含占位符）")

print("\n【4】仓库元信息")
info = api(f"/repos/{REPO}")
print(f"   名称: {info['full_name']}")
print(f"   可见性: {info['visibility']}")
print(f"   默认分支: {info['default_branch']}")
print(f"   描述: {info.get('description') or '(空)'}")

print("\n" + "=" * 56)
print(f"  🎉 仓库地址: https://github.com/{REPO}")
print("=" * 56)
