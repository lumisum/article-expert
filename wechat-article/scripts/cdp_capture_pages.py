#!/usr/bin/env python3
"""Capture rendered web pages through a CDP remote-debugging browser."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import http.client
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import websockets

from path_utils import reject_literal_tilde, wechat_workspace_root


DEFAULT_BROWSER_JSON_URL = "http://127.0.0.1:19222/json/list"
CDP_ENV_KEYS = ("BENEVA_CDP_JSON_URL", "BENEVA_BROWSER_JSON_URL", "CDP_BROWSER_JSON_URL")
NAVIGATION_RETRY_ERRORS = (
    "Execution context was destroyed",
    "Cannot find default execution context",
    "Inspected target navigated or closed",
    "Target closed",
    "no close frame received or sent",
)


def default_browser_json_url() -> str:
    for key in CDP_ENV_KEYS:
        value = os.environ.get(key)
        if value:
            return value
    return DEFAULT_BROWSER_JSON_URL


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def safe_name(value: str, index: int) -> str:
    parsed = urlparse(value)
    base = f"{parsed.netloc}{parsed.path}".strip("/") or f"page-{index:02d}"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-")
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"{base[:78] or 'page'}-{digest}.md"


def validate_out_dir(path: Path) -> Path:
    out_dir = path.resolve()
    reject_literal_tilde(out_dir)
    root = wechat_workspace_root().resolve()
    try:
        relative = out_dir.relative_to(root)
    except ValueError:
        fail(f"--out-dir must be under the real wechat workspace: {root}")

    parts = relative.parts
    if len(parts) >= 2 and parts[0] == "topics" and parts[1].startswith("_"):
        fail(
            "Stage runtime capture directories must belong to a concrete topic. "
            f"Invalid direct topics runtime path: {out_dir}. Use "
            f"{root}/topic_scans/[scan_id]/research/raw_pages/ for Stage 0 or "
            f"{root}/topics/[topic_id]/research/raw_pages/ for Stage 1-3."
        )
    if len(parts) == 1 and parts[0] in {"topics", "topic_scans"}:
        fail(f"--out-dir cannot be a workspace collection root: {out_dir}")
    return out_dir


def http_json(method: str, url: str, timeout: int = 8) -> Any:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail(f"Invalid URL: {url}")
    connection_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    conn = connection_class(parsed.netloc, timeout=timeout)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        data = response.read().decode("utf-8")
    finally:
        conn.close()
    if response.status >= 400:
        fail(f"HTTP {response.status} from {url}: {data[:500]}")
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        fail(f"Invalid JSON from {url}: {data[:500]}")


def browser_base_url(browser_json_url: str) -> str:
    parsed = urlparse(browser_json_url)
    if not parsed.scheme or not parsed.netloc:
        fail(f"Invalid --browser-json-url: {browser_json_url}")
    return f"{parsed.scheme}://{parsed.netloc}"


def open_tab(browser_json_url: str, url: str) -> dict[str, Any]:
    target = f"{browser_base_url(browser_json_url)}/json/new?{quote(url, safe='')}"
    tab = http_json("PUT", target, timeout=8)
    if not isinstance(tab, dict) or not tab.get("webSocketDebuggerUrl"):
        fail(f"CDP /json/new returned unexpected tab data for {url}: {tab}")
    return tab


def load_tabs(browser_json_url: str) -> list[dict[str, Any]]:
    tabs = http_json("GET", browser_json_url, timeout=8)
    if not isinstance(tabs, list):
        fail(f"CDP endpoint returned non-list tab data from {browser_json_url}")
    return tabs


def tab_ws_url(browser_json_url: str, tab_id: str) -> str | None:
    for tab in load_tabs(browser_json_url):
        if str(tab.get("id") or "") == str(tab_id):
            return tab.get("webSocketDebuggerUrl")
    return None


def is_navigation_error(exc: Exception) -> bool:
    message = str(exc)
    return any(text in message for text in NAVIGATION_RETRY_ERRORS)


async def browser_eval(ws_url: str, expression: str, timeout_ms: int = 120000) -> dict[str, Any]:
    async with websockets.connect(ws_url, max_size=80_000_000) as ws:
        seq = 0

        async def call(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
            nonlocal seq
            seq += 1
            await ws.send(json.dumps({"id": seq, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == seq:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        await call("Runtime.enable")
        return await call(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": True, "returnByValue": True, "timeout": timeout_ms},
        )


async def browser_eval_with_navigation_retry(
    browser_json_url: str,
    tab_id: str | None,
    ws_url: str,
    expression: str,
    timeout_ms: int = 120000,
    retries: int = 4,
) -> dict[str, Any]:
    current_ws_url = ws_url
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        if attempt:
            await asyncio.sleep(min(6.0, 1.5 * attempt))
        try:
            return await browser_eval(current_ws_url, expression, timeout_ms=timeout_ms)
        except Exception as exc:
            last_error = exc
            if not is_navigation_error(exc):
                raise
            if tab_id:
                refreshed = tab_ws_url(browser_json_url, tab_id)
                if refreshed:
                    current_ws_url = refreshed
    raise last_error or RuntimeError("browser_eval failed after navigation retry")


def capture_expression(wait_ms: int, max_chars: int) -> str:
    return f"""
(async () => {{
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const startedAt = Date.now();
  while ((location.href === 'about:blank' || document.readyState === 'loading' || !document.body) && Date.now() - startedAt < 45000) {{
    await sleep(250);
  }}
  await sleep({wait_ms});
  const text = (document.body && document.body.innerText || '').replace(/\\n{{3,}}/g, '\\n\\n').trim();
  const links = Array.from(document.querySelectorAll('a[href]')).slice(0, 80).map((a) => ({{
    text: (a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 160),
    href: a.href
  }})).filter((x) => x.text || x.href);
  const metas = Array.from(document.querySelectorAll('meta')).map((m) => ({{
    name: m.getAttribute('name') || m.getAttribute('property') || '',
    content: m.getAttribute('content') || ''
  }})).filter((x) => x.name && x.content).slice(0, 80);
  return {{
    ok: true,
    title: document.title || '',
    url: location.href,
    captured_at: new Date().toISOString(),
    text: text.slice(0, {max_chars}),
    text_chars: text.length,
    links,
    metas
  }};
}})()
"""


def page_to_markdown(url: str, payload: dict[str, Any]) -> str:
    links = payload.get("links") if isinstance(payload.get("links"), list) else []
    metas = payload.get("metas") if isinstance(payload.get("metas"), list) else []
    lines = [
        "---",
        f"source_url: {url}",
        f"final_url: {payload.get('url', '')}",
        "access_method: cdp",
        f"accessed_at: {payload.get('captured_at', '')}",
        f"title: {json.dumps(payload.get('title', ''), ensure_ascii=False)}",
        f"text_chars: {payload.get('text_chars', 0)}",
        "---",
        "",
        "# Rendered Page Snapshot",
        "",
        "## Visible Text",
        "",
        str(payload.get("text") or "").strip(),
        "",
        "## Page Links",
        "",
    ]
    for item in links:
        text = str(item.get("text") or "").strip()
        href = str(item.get("href") or "").strip()
        if href:
            lines.append(f"- {text}: {href}" if text else f"- {href}")
    lines += ["", "## Meta Tags", ""]
    for item in metas:
        lines.append(f"- {item.get('name')}: {item.get('content')}")
    return "\n".join(lines).rstrip() + "\n"


async def main_async() -> int:
    parser = argparse.ArgumentParser(description="Capture rendered pages through a CDP browser.")
    parser.add_argument("--url", action="append", default=[], help="URL to capture. Can be repeated.")
    parser.add_argument("--url-file", help="Text file with one URL per line.")
    parser.add_argument("--out-dir", required=True, help="Directory where markdown snapshots will be written.")
    parser.add_argument("--browser-json-url", default=default_browser_json_url())
    parser.add_argument("--wait-ms", type=int, default=3500)
    parser.add_argument("--max-chars", type=int, default=30000)
    args = parser.parse_args()

    urls = list(args.url)
    if args.url_file:
        urls.extend(
            line.strip()
            for line in Path(args.url_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    if not urls:
        fail("Pass at least one --url or --url-file.")

    out_dir = validate_out_dir(Path(args.out_dir).expanduser())
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "cdp_capture_manifest.json"
    existing_manifest: list[dict[str, Any]] = []
    if manifest_path.is_file():
        try:
            loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"Invalid existing capture manifest {manifest_path}: {exc}")
        if not isinstance(loaded_manifest, list):
            fail(f"Existing capture manifest must be a list: {manifest_path}")
        existing_manifest = [
            item for item in loaded_manifest if isinstance(item, dict)
        ]
    current_run: list[dict[str, Any]] = []
    expression = capture_expression(max(0, args.wait_ms), max(1000, args.max_chars))

    for index, url in enumerate(urls, start=1):
        started = time.time()
        try:
            tab = open_tab(args.browser_json_url, url)
            result = await browser_eval_with_navigation_retry(
                args.browser_json_url,
                str(tab.get("id") or ""),
                tab["webSocketDebuggerUrl"],
                expression,
            )
            value = result.get("result", {}).get("value") or {}
            if not value.get("ok"):
                raise RuntimeError(json.dumps(value, ensure_ascii=False))
            final_url = str(value.get("url") or "").strip()
            visible_text = str(value.get("text") or "").strip()
            if not final_url or final_url == "about:blank":
                raise RuntimeError("Page never left about:blank before capture.")
            if len(visible_text) < 120:
                raise RuntimeError(
                    f"Rendered page text is too short to preserve as evidence: "
                    f"{len(visible_text)} characters."
                )
            path = out_dir / safe_name(url, index)
            path.write_text(page_to_markdown(url, value), encoding="utf-8")
            current_run.append({
                "url": url,
                "final_url": value.get("url"),
                "title": value.get("title"),
                "path": str(path),
                "status": "captured",
                "captured_at": value.get("captured_at"),
                "elapsed_seconds": round(time.time() - started, 2),
            })
        except Exception as exc:
            current_run.append({
                "url": url,
                "status": "failed",
                "error": str(exc),
                "elapsed_seconds": round(time.time() - started, 2),
            })

    manifest = [*existing_manifest, *current_run]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "out_dir": str(out_dir),
        "manifest": str(manifest_path),
        "pages": current_run,
        "total_manifest_records": len(manifest),
    }, ensure_ascii=False, indent=2))
    return 0 if all(item["status"] == "captured" for item in current_run) else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async()))
