#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过 GitHub API 推送整个仓库（绕过被墙的 git 通道）
策略：
  1) 空仓库先用 Contents API 创建首个文件完成初始化（GitHub 限制：空仓库无法用 Git Data API）
  2) 其余文件用 Git Data API 一次性提交（blobs → tree(base_tree) → commit → 更新 ref）
用法：python push_via_api.py
前提：token 放在 D:\\ModelShield\\.token
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, ".token")
GIT = r"D:\tools\MinGit\cmd\git.exe"
COMMIT_MSG = """feat: 模盾 ModelShield v0.2 - AI安全体检平台

- 攻击语料库 71 条（提示词注入/越狱/敏感信息泄露/工具滥用/有害内容/幻觉虚构）
- 红队引擎：真实 API 目标 + 离线模拟靶子双模式
- 判定引擎 + 自动生成《AI 安全体检报告》（含证据链与修复建议）
- Web 平台（Flask）+ 接口冒烟测试
- 实测对比：裸奔版 36/100（43条攻破） vs 加固版 100/100
"""


def read_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"[!] 未找到 token 文件: {TOKEN_FILE}")
        sys.exit(1)
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def api(method, path, token, data=None):
    url = API + path
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "ModelShield-Pusher")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        raise RuntimeError(f"HTTP {e.code}: {detail}")


def git_files():
    """-z 用 NUL 分隔且不做转义，避免中文文件名被八进制转义"""
    out = subprocess.run([GIT, "ls-files", "-z"], cwd=ROOT, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("git ls-files 失败: " + out.stderr.decode("utf-8", "ignore"))
    raw = out.stdout.decode("utf-8")
    return [p for p in raw.split("\0") if p.strip()]


def read_b64(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def main():
    token = read_token()
    print("[*] 校验 Token ...")
    me = api("GET", "/user", token)
    login = me["login"]
    print(f"    ✅ 已认证: {login}")

    repo = None
    try:
        for r in api("GET", "/user/repos?per_page=100&sort=updated", token):
            if r["name"].lower() == "modelshield":
                repo = r["full_name"]
                break
    except Exception as e:
        print(f"    ⚠️ 列出仓库失败: {e}")
    if repo is None:
        repo = f"{login}/ModelShield"
    info = api("GET", f"/repos/{repo}", token)
    branch = info.get("default_branch", "main")
    print(f"[*] 目标仓库: {repo}  (默认分支: {branch})")

    files = git_files()
    print(f"[*] 待推送文件: {len(files)} 个\n")

    # ---------- 阶段 1：空仓库初始化 ----------
    need_init = False
    try:
        api("GET", f"/repos/{repo}/git/ref/heads/{branch}", token)
    except RuntimeError as e:
        if "404" in str(e) or "409" in str(e):
            need_init = True
        else:
            raise
    if need_init:
        first = files[0]
        print(f"[*] 空仓库 → 用 Contents API 初始化（{first}）")
        api("PUT", f"/repos/{repo}/contents/{urllib.parse.quote(first)}", token,
            {"message": "chore: 初始化仓库", "content": read_b64(first), "branch": branch})
        files = files[1:]
        print(f"    ✅ 初始化完成，剩余 {len(files)} 个文件")

    if not files:
        print("\n🎉 推送完成（仅初始化文件）")
        return

    # ---------- 阶段 2：批量提交 ----------
    ref = api("GET", f"/repos/{repo}/git/ref/heads/{branch}", token)
    parent_sha = ref["object"]["sha"]
    base_commit = api("GET", f"/repos/{repo}/git/commits/{parent_sha}", token)
    base_tree = base_commit["tree"]["sha"]
    print(f"[*] 当前 HEAD: {parent_sha[:10]}")

    tree_items = []
    for f in files:
        blob = api("POST", f"/repos/{repo}/git/blobs", token,
                   {"content": read_b64(f), "encoding": "base64"})
        tree_items.append({"path": f.replace("\\", "/"), "mode": "100644",
                           "type": "blob", "sha": blob["sha"]})
        print(f"    + {f}")

    tree = api("POST", f"/repos/{repo}/git/trees", token,
               {"base_tree": base_tree, "tree": tree_items})
    commit = api("POST", f"/repos/{repo}/git/commits", token,
                 {"message": COMMIT_MSG, "tree": tree["sha"], "parents": [parent_sha]})
    api("PATCH", f"/repos/{repo}/git/refs/heads/{branch}", token,
        {"sha": commit["sha"], "force": False})
    print(f"\n[*] commit: {commit['sha'][:10]}")

    # ---------- 校验 ----------
    items = api("GET", f"/repos/{repo}/contents/", token)
    print(f"[*] 远程根目录条目: {len(items)} 个")
    print(f"\n🎉 推送成功！https://github.com/{repo}")


if __name__ == "__main__":
    main()
