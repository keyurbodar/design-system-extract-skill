#!/usr/bin/env python3
"""Minimal Doop MCP HTTP client. Token comes from the DOOP_TOKEN environment variable; it is never stored in this repo.
usage: doop_cli.py list-tools | doop_cli.py call <tool> '<json args>' [--out file]"""
import json
import os
import sys
import urllib.request

URL = "https://doop.design/mcp"
TOKEN = os.environ.get("DOOP_TOKEN")


def call_mcp(method, params=None, req_id=1):
    if not TOKEN:
        raise RuntimeError("DOOP_TOKEN is not set")
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        ct = resp.headers.get("Content-Type", "")
        if "text/event-stream" in ct:
            # Extract last JSON data line
            last = None
            for line in raw.splitlines():
                if line.startswith("data:"):
                    d = line[5:].strip()
                    if d:
                        last = d
            return json.loads(last) if last else {"raw": raw}
        return json.loads(raw)


def call_tool(name, arguments=None):
    res = call_mcp("tools/call", {"name": name, "arguments": arguments or {}})
    if "error" in res:
        raise RuntimeError(f"MCP error: {json.dumps(res['error'])}")
    result = res.get("result", {})
    content = result.get("content", [])
    texts = []
    for item in content:
        if item.get("type") == "text":
            texts.append(item.get("text", ""))
        elif item.get("type") == "image":
            texts.append(f"[IMAGE {item.get('mimeType')} len={len(item.get('data',''))}]")
    return "\n".join(texts), result.get("isError", False)


def main():
    if len(sys.argv) < 2:
        print("Usage: doop_cli.py <list-tools|call> [tool_name] [json_args_or_@file] [--out file]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list-tools":
        res = call_mcp("tools/list", {})
        for t in res.get("result", {}).get("tools", []):
            print(f"{t['name']}: {t.get('title','')}")
        return
    if cmd == "call":
        tool_name = sys.argv[2]
        args = {}
        out_path = None
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--out":
                out_path = sys.argv[i + 1]
                i += 2
            else:
                arg_str = sys.argv[i]
                if arg_str.startswith("@"):
                    with open(arg_str[1:], "r", encoding="utf-8") as f:
                        args = json.load(f)
                else:
                    args = json.loads(arg_str)
                i += 1
        text, is_err = call_tool(tool_name, args)
        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Wrote {len(text)} chars to {out_path} (isError={is_err})")
        else:
            print(text)
        if is_err:
            sys.exit(2)
        return
    print(f"Unknown cmd: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
