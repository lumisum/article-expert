#!/usr/bin/env python3
"""Convert final_article.md to polished WeChat paste-safe HTML.

Design goal: a precise technology-business editorial page with visible data
rhythm before the reader reads a sentence. Everything is inline-styled with WeChat-editor-safe CSS only
(no external stylesheets, no scripts, no absolute positioning, no flex).

Color roles are taken from the article image palette when available:
- section (##): article accent
- subsection (### / 第N步): first supporting color
- emphasis (punch / bold): second supporting color

The fragment intentionally emits no page background or external stylesheet.
Local editorial components use transparent surfaces, precise borders and small radius;
the code component uses a dark editor-window treatment for reliable contrast.

Core visual formats:
1. opening lead card           (data-wa-format="opening-lead")
2. numbered major section head (data-wa-format="section-title")  # 圆形 01 徽章 + 标题
3. subsection heading          (data-wa-format="subsection-title")
4. punch line paragraph        (data-wa-format="punch")
5. quote                       (data-wa-format="quote")
6. list / table                (data-wa-format="list" / "table")
7. fenced code block           (data-wa-format="code-block")
8. closing reader questions    (data-wa-format="reader-questions")

The visual rhythm is built from whitespace, typography, outlined chapter badges,
semantic emphasis, restrained rules, and alternating short/long statement treatments.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

from path_utils import ensure_topic_dir, expand_user_path, latest_workflow_path

try:
    from pygments import highlight as pygments_highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
except ImportError:  # Keep plain-code fallback if a minimal runtime lacks Pygments.
    pygments_highlight = None
    HtmlFormatter = None
    get_lexer_by_name = None


DEFAULT_ACCENT = "#0071E3"

# System text colors inherit the phone/editor light or dark canvas. Component
# surfaces may use local colors; the page itself never paints a background.
INK = "CanvasText"
INK_SECONDARY = "CanvasText"
HAIRLINE = "#b9c0c9"

PUNCH_MAX_CHARS = 20

HORIZONTAL_RULE_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
STEP_SUBTITLE_RE = re.compile(r"^第[一二三四五六七八九十百零〇\d]+步[，,：:].+")
IMAGE_MARKER_RE = re.compile(
    r"^(?:<!--\s*IMAGE:([A-Za-z0-9_\-]+)\s*-->|\[IMAGE_PLACEHOLDER:\s*([A-Za-z0-9_\-]+)\s*\])$",
    flags=re.IGNORECASE,
)
DEPTH_MARKER_RE = re.compile(
    r"^<!--\s*(?:DESCENT:L\d+:C\d+(?:\s*,\s*C\d+)*|SPARK:S\d+|REBOUND)\s*-->$",
    flags=re.IGNORECASE,
)
DATA_MARKER_RE = re.compile(
    r"^<!--\s*DATA:N\d{2,}(?:\s*,\s*N\d{2,})*\s*-->$",
    flags=re.IGNORECASE,
)
NON_IMAGE_CONSTRUCTION_RE = re.compile(
    r"<!--\s*(?:DATA:[^>]*|USER:[^>]*|DESCENT:[^>]*|SPARK:[^>]*|REBOUND)\s*-->",
    flags=re.IGNORECASE,
)
USER_MARKER_RE = re.compile(
    r"^<!--\s*USER:U\d{2,}(?:\s*,\s*U\d{2,})*\s*-->$",
    flags=re.IGNORECASE,
)
ANY_IMAGE_COMMENT_RE = re.compile(
    r"<!--\s*IMAGE:[A-Za-z0-9_\-]+\s*-->",
    flags=re.IGNORECASE,
)
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^[^\]\n]+\]")
FOOTNOTE_DEFINITION_RE = re.compile(r"^\s*\[\^[^\]\n]+\]:")
IMAGE_MIN_BODY_BLOCKS = 2
IMAGE_MIN_CONTEXT_CHARS = 140
IMAGE_MAX_BODY_BLOCKS = 4
CODE_FENCE_OPEN_RE = re.compile(r"^(`{3,}|~{3,})\s*([^\s`~]+)?(?:\s+.*)?$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def resolve_topic_dir(cli_topic_dir: str | None) -> Path:
    if cli_topic_dir:
        return ensure_topic_dir(expand_user_path(cli_topic_dir))

    cwd = Path.cwd().resolve()
    if (cwd / "article" / "final_article.md").exists():
        return ensure_topic_dir(cwd)

    runtime = load_json(latest_workflow_path(), {})
    for key in ("topic_dir", "current_topic_dir", "latest_topic_dir"):
        value = runtime.get(key)
        if value:
            return ensure_topic_dir(expand_user_path(str(value)))

    fail("Cannot find topic directory. Run from a topic directory or pass --topic-dir.")


def extract_hex(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r"#[0-9A-Fa-f]{6}", text)
    return match.group(0).upper() if match else None


def choose_palette(topic_dir: Path) -> tuple[str, list[str]]:
    package = load_json(topic_dir / "assets" / "title_cover_package.json", {})
    if isinstance(package, dict):
        cover = package.get("cover_prompt")
        if isinstance(cover, dict):
            accent = extract_hex(str(cover.get("accent_color", "")))
            if accent:
                supporting = [
                    color
                    for value in cover.get("supporting_colors", [])
                    if (color := extract_hex(str(value)))
                ]
                return accent, supporting

    prompts_path = topic_dir / "assets" / "image_prompts.jsonl"
    if prompts_path.exists():
        for line in prompts_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            accent = extract_hex(str(item.get("accent_color", "")))
            if accent:
                supporting = [
                    color
                    for value in item.get("supporting_colors", [])
                    if (color := extract_hex(str(value)))
                ]
                return accent, supporting
    return DEFAULT_ACCENT, ["#5E5CE6", "#FF375F", "#34C759"]


def article_mode(topic_dir: Path) -> str:
    pack = load_json(topic_dir / "research" / "source_pack.json", {})
    profile = pack.get("article_profile") if isinstance(pack, dict) else None
    if isinstance(profile, dict):
        mode = str(profile.get("mode") or "").strip().lower()
        if mode and mode != "business_investment":
            fail(
                "businvet-article only renders "
                "article_profile.mode=business_investment."
            )
    return "business_investment"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    max_c, min_c = max(rf, gf, bf), min(rf, gf, bf)
    lightness = (max_c + min_c) / 2.0
    if max_c == min_c:
        return 0.0, 0.0, lightness
    delta = max_c - min_c
    saturation = delta / (2.0 - max_c - min_c) if lightness > 0.5 else delta / (max_c + min_c)
    if max_c == rf:
        hue = ((gf - bf) / delta) + (6.0 if gf < bf else 0.0)
    elif max_c == gf:
        hue = ((bf - rf) / delta) + 2.0
    else:
        hue = ((rf - gf) / delta) + 4.0
    return hue * 60.0, saturation, lightness


def hsl_to_rgb(h: float, s: float, lightness: float) -> tuple[int, int, int]:
    h = h % 360.0

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    if s == 0:
        value = int(round(lightness * 255))
        return value, value, value
    q = lightness * (1 + s) if lightness < 0.5 else lightness + s - lightness * s
    p = 2 * lightness - q
    hk = h / 360.0
    r = hue_to_rgb(p, q, hk + 1 / 3)
    g = hue_to_rgb(p, q, hk)
    b = hue_to_rgb(p, q, hk - 1 / 3)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def shift_hue(
    hex_color: str,
    degrees: float,
    saturation: float | None = None,
    lightness: float | None = None,
) -> str:
    h, s, l = rgb_to_hsl(*hex_to_rgb(hex_color))
    h = (h + degrees) % 360.0
    if saturation is not None:
        s = saturation
    if lightness is not None:
        l = lightness
    # Keep accents mid-sat / mid-dark so they read on soft paper and against dark chrome.
    s = max(0.40, min(0.68, s))
    l = max(0.30, min(0.44, l))
    return rgb_to_hex(*hsl_to_rgb(h, s, l))


def readable_accent(hex_color: str) -> str:
    """Preserve hue while keeping borders and text legible on white."""
    h, s, lightness = rgb_to_hsl(*hex_to_rgb(hex_color))
    if lightness <= 0.48 and s >= 0.32:
        return hex_color.upper()
    return rgb_to_hex(*hsl_to_rgb(h, max(0.40, min(0.68, s)), min(0.43, lightness)))


def mix_hex(foreground: str, background: str, keep: float) -> str:
    """Blend foreground into background. keep=1 keeps foreground; keep=0 yields background."""
    fr, fg, fb = hex_to_rgb(foreground)
    br, bg, bb = hex_to_rgb(background)
    keep = max(0.0, min(1.0, keep))
    r = int(round(fr * keep + br * (1 - keep)))
    g = int(round(fg * keep + bg * (1 - keep)))
    b = int(round(fb * keep + bb * (1 - keep)))
    return rgb_to_hex(r, g, b)


def border_tint(hex_color: str) -> str:
    return mix_hex(hex_color, HAIRLINE, 0.35)


def convert_inline(text: str, theme: "Theme") -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\*\*(.*?)\*\*",
        rf'<strong style="color: {theme.ink}; font-weight: 850; border-bottom: 1px solid {theme.emphasis_soft}; '
        rf'padding-bottom: 2px;">\1</strong>',
        escaped,
    )
    escaped = re.sub(
        r"\*(.*?)\*",
        rf'<em style="color: {theme.emphasis}; font-style: normal; font-weight: 700;">\1</em>',
        escaped,
    )
    escaped = re.sub(
        r"`(.*?)`",
        rf'<code style="font-family: Menlo, Monaco, Consolas, monospace; font-size: 15px; '
        rf'padding: 1px 5px; border: 1px solid {theme.hairline}; border-radius: 2px; '
        rf'background: {theme.surface_alt}; color: {theme.section};">\1</code>',
        escaped,
    )
    return escaped


def nonspace_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def sanitize_construction_markers(md_text: str) -> str:
    """Keep image anchors while removing build markers and publishing footnotes."""
    def strip_comment(match: re.Match[str]) -> str:
        comment = match.group(0).strip()
        return comment if IMAGE_MARKER_RE.fullmatch(comment) else ""

    # Construction notes can span several lines. Remove every HTML comment
    # except a valid image anchor before block parsing so no internal planning
    # prose can ever become visible article text.
    md_text = re.sub(r"<!--[\s\S]*?-->", strip_comment, md_text)
    clean_lines: list[str] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if FOOTNOTE_DEFINITION_RE.match(line):
            continue
        if IMAGE_MARKER_RE.fullmatch(stripped):
            clean_lines.append(stripped)
            continue
        line = NON_IMAGE_CONSTRUCTION_RE.sub("", line)
        line = ANY_IMAGE_COMMENT_RE.sub("", line)
        line = FOOTNOTE_REFERENCE_RE.sub("", line)
        clean_lines.append(line.rstrip())
    return "\n".join(clean_lines)


def parse_blocks(md_text: str) -> list[tuple[str, list[str]]]:
    md_text = sanitize_construction_markers(md_text)
    blocks: list[tuple[str, list[str]]] = []
    current_type: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_type, current_lines
        if current_lines:
            blocks.append((current_type or "paragraph", current_lines))
            current_lines = []
            current_type = None

    code_fence_char: str | None = None
    code_fence_len = 0
    code_language = ""
    for line in md_text.splitlines():
        stripped = line.strip()
        if code_fence_char is not None:
            closing = re.fullmatch(
                rf"{re.escape(code_fence_char)}{{{code_fence_len},}}\s*",
                stripped,
            )
            if closing:
                blocks.append(("code", [code_language, *current_lines]))
                current_lines = []
                current_type = None
                code_fence_char = None
                code_fence_len = 0
                code_language = ""
                continue
            current_lines.append(line)
            continue
        fence = CODE_FENCE_OPEN_RE.fullmatch(stripped)
        if fence:
            flush()
            token = fence.group(1)
            code_fence_char = token[0]
            code_fence_len = len(token)
            code_language = (fence.group(2) or "").strip()
            current_lines = []
            current_type = None
            continue
        if not stripped:
            # Keep ordered items together across optional Markdown blank lines;
            # WeChat can restart an <ol> marker when each item becomes a new list.
            if current_type != "list":
                flush()
            continue
        if (
            DEPTH_MARKER_RE.fullmatch(stripped)
            or DATA_MARKER_RE.fullmatch(stripped)
            or USER_MARKER_RE.fullmatch(stripped)
        ):
            flush()
            continue
        if HORIZONTAL_RULE_RE.fullmatch(stripped):
            flush()
            continue
        if stripped.startswith("#"):
            flush()
            blocks.append(("heading", [line]))
            continue
        if stripped.startswith(">"):
            if current_type != "quote":
                flush()
                current_type = "quote"
            current_lines.append(stripped[1:].strip())
            continue
        if stripped.startswith("|"):
            if current_type != "table":
                flush()
                current_type = "table"
            current_lines.append(line)
            continue
        if re.match(r"^([\*\-\+]\s+|\d+\.\s+)", stripped):
            if current_type != "list":
                flush()
                current_type = "list"
            current_lines.append(line)
            continue
        if current_type != "paragraph":
            flush()
            current_type = "paragraph"
        current_lines.append(line)
    if code_fence_char is not None:
        blocks.append(("code", [code_language, *current_lines]))
        current_lines = []
        current_type = None
    flush()
    return blocks


MAX_READER_QUESTIONS = 3


class Theme:
    """Article-aware editorial palette with a dark editor-style code component."""

    def __init__(
        self,
        accent: str,
        supporting: list[str] | None = None,
        *,
        mode: str = "business_investment",
    ) -> None:
        supporting = [value.upper() for value in (supporting or []) if value.upper() != accent.upper()]
        self.mode = mode
        self.is_life = False
        self.accent = accent.upper()
        if self.is_life:
            # A restrained editorial palette: weathered copper, rain blue and
            # graphite. It carries lived time without turning the article beige.
            self.section = "#8A5942"
            self.subsection = "#426579"
            self.emphasis = "#A66A2C"
            self.tertiary = "#66625D"
        else:
            self.section = readable_accent(self.accent)
            self.subsection = readable_accent(
                supporting[0] if supporting else shift_hue(self.accent, 42)
            )
            self.emphasis = readable_accent(
                supporting[1] if len(supporting) > 1 else shift_hue(self.accent, -38)
            )
            self.tertiary = readable_accent(
                supporting[2] if len(supporting) > 2 else shift_hue(self.accent, 110)
            )
        # Follow the phone/editor canvas instead of baking in a light-mode text
        # color. Decorative accents remain explicit; readable prose adapts.
        self.ink = INK
        self.ink_secondary = INK_SECONDARY
        self.hairline = "#D2D2D7"
        self.border = "#D2D2D7"
        self.surface = "#F5F5F7"
        self.surface_alt = "#E8E8ED"
        self.muted = "#86868B"
        self.emphasis_soft = border_tint(self.emphasis)
        self.code_background = "#1D1D1F"
        self.code_header = "#2C2C2E"
        self.code_border = "#48484A"
        self.code_ink = "#F5F5F7"
        self.code_muted = "#A1A1A6"
        self.code_shadow = "0 8px 20px rgba(0, 0, 0, 0.14)"


def render_subsection_title(text: str, theme: Theme) -> str:
    if theme.is_life:
        return (
            f'<p data-wa-format="subsection-title" data-wa-variant="life-turn" '
            f'style="margin: 38px 0 16px; padding: 0 0 7px; '
            f'border-bottom: 1px solid {theme.hairline}; font-size: 15px; line-height: 1.7; '
            f'color: {theme.ink}; font-weight: 800;">'
            f'<span style="display: inline-block; margin-right: 9px; color: {theme.emphasis}; '
            f'font-size: 15px;">◆</span>{convert_inline(text, theme)}</p>'
        )
    return (
        f'<p data-wa-format="subsection-title" style="margin: 36px 0 15px; padding: 0 0 8px; '
        f'border-bottom: 1px solid {theme.hairline}; '
        f'font-size: 15px; line-height: 1.6; color: {theme.ink}; font-weight: 800;">'
        f'<span style="display: inline-block; width: 22px; margin-right: 10px; '
        f'border-top: 3px solid {theme.subsection}; vertical-align: 5px;">&nbsp;</span>'
        f'{convert_inline(text, theme)}</p>'
    )


def looks_like_step_subtitle(text: str) -> bool:
    return bool(STEP_SUBTITLE_RE.match(text.strip()))


def clean_section_title(text: str) -> str:
    """Remove author-supplied section numbering before rendering 【NN】 badges."""
    cleaned = text.strip()
    # Strip 【01】/【1】 and 一、/1. style prefixes (may appear twice if author already numbered).
    cleaned = re.sub(r"^(?:【\s*\d+\s*】\s*)+", "", cleaned)
    cleaned = re.sub(r"^(?:[一二三四五六七八九十百千万]+|\d+)[、.．:：\s]+", "", cleaned)
    cleaned = re.sub(r"^(?:【\s*\d+\s*】\s*)+", "", cleaned)
    if len(cleaned) >= 2 and cleaned[0] in "\"'“‘「『" and cleaned[-1] in "\"'”’」』":
        cleaned = cleaned[1:-1].strip()
    return cleaned or text.strip()


def clean_quote_lead(text: str) -> str:
    """Avoid duplicating the opening quote rendered by the quote component."""
    return text.lstrip().lstrip('"\'“‘「『').lstrip()


def render_article_title(text: str, theme: Theme) -> str:
    if theme.is_life:
        return (
            f'<section data-wa-format="article-title" data-wa-variant="life-editorial" '
            f'style="margin: 12px 0 31px; padding: 18px 5px 15px; '
            f'border-top: 1px solid {theme.hairline}; border-bottom: 1px solid {theme.hairline}; '
            f'box-sizing: border-box; text-align: center;">\n'
            f'  <p style="margin: 0 auto 11px; width: 54px; font-size: 15px; line-height: 1; '
            f'border-top: 3px solid {theme.section};">&nbsp;</p>\n'
            f'  <h1 style="font-size: 15px; line-height: 1.7; color: {theme.ink}; font-weight: 900; '
            f'margin: 0; padding: 0; text-align: center; letter-spacing: 0;">'
            f'{convert_inline(text, theme)}</h1>\n'
            f'  <p style="margin: 12px auto 0; width: 86px; font-size: 15px; line-height: 1; '
            f'border-top: 1px solid {theme.subsection};">&nbsp;</p>\n'
            f'</section>'
        )
    return (
        f'<section data-wa-format="article-title" data-wa-variant="business-signal" '
        f'style="margin: 10px 0 32px; padding: 0; border-top: 1px solid {theme.hairline}; '
        f'border-right: 1px solid {theme.hairline}; border-bottom: 1px solid {theme.hairline}; '
        f'border-left: 4px solid {theme.section}; box-sizing: border-box;">'
        f'<p style="margin: 0; padding: 0; height: 5px; line-height: 1; font-size: 0;">'
        f'<span style="display: inline-block; width: 46%; border-top: 4px solid {theme.section};"></span>'
        f'<span style="display: inline-block; width: 31%; border-top: 4px solid {theme.subsection};"></span>'
        f'<span style="display: inline-block; width: 23%; border-top: 4px solid {theme.emphasis};"></span>'
        f'</p>'
        f'<h1 style="font-size: 15px; line-height: 1.65; color: {theme.ink}; font-weight: 900; '
        f'margin: 0; padding: 19px 18px 20px; text-align: left; letter-spacing: 0; '
        f'box-sizing: border-box;">{convert_inline(text, theme)}</h1>'
        f'</section>'
    )


def render_quote(text: str, theme: Theme) -> str:
    if theme.is_life:
        return (
            f'<section data-wa-format="quote" data-wa-variant="life-memory" '
            f'style="margin: 34px 0; padding: 17px 16px 16px 19px; '
            f'border-top: 1px solid {theme.hairline}; border-right: 1px solid {theme.hairline}; '
            f'border-bottom: 1px solid {theme.hairline}; border-left: 3px solid {theme.section}; '
            f'border-radius: 0; box-sizing: border-box;">\n'
            f'  <p style="margin: 0; font-size: 15px; line-height: 1.9; color: {theme.ink_secondary};">'
            f'<span style="color: {theme.emphasis}; font-size: 15px; font-weight: 900; '
            f'margin-right: 5px;">“</span>{convert_inline(text, theme)}</p>\n'
            f'</section>'
        )
    return (
        f'<section data-wa-format="quote" style="margin: 30px 0; padding: 16px 18px; '
        f'border-top: 1px solid {theme.subsection}; border-right: 1px solid {theme.hairline}; '
        f'border-bottom: 1px solid {theme.hairline}; border-left: 4px solid {theme.subsection}; '
        f'border-radius: 2px; box-sizing: border-box;">\n'
        f'  <p style="margin: 0; font-size: 15px; line-height: 1.85; color: {theme.ink_secondary};">'
        f'<span style="color: {theme.subsection}; font-size: 15px; line-height: 0; '
        f'font-weight: 900; margin-right: 4px;">“</span>'
        f'{convert_inline(text, theme)}</p>\n'
        f'</section>'
    )


def render_opening_lead(text: str, theme: Theme) -> str:
    """Editorial lead with no fragile background fill."""
    if theme.is_life:
        return (
            f'<section data-wa-format="opening-lead" data-wa-variant="life-scene" '
            f'style="margin: 10px 0 38px; padding: 17px 3px 15px 18px; '
            f'border-top: 1px solid {theme.hairline}; border-right: 0; '
            f'border-bottom: 1px solid {theme.hairline}; border-left: 3px solid {theme.section}; '
            f'border-radius: 0; box-sizing: border-box;">\n'
            f'    <p style="margin: 0; font-size: 15px; line-height: 1.9; color: {theme.ink}; '
            f'font-weight: 700; text-align: left;">{convert_inline(text, theme)}</p>\n'
            f'</section>'
        )
    return (
        f'<section data-wa-format="opening-lead" data-wa-variant="business-brief" '
        f'style="margin: 12px 0 38px; padding: 18px 18px 17px; '
        f'border-top: 2px solid {theme.section}; border-right: 1px solid {theme.hairline}; '
        f'border-bottom: 1px solid {theme.hairline}; '
        f'border-left: 4px solid {theme.emphasis}; border-radius: 2px; box-sizing: border-box;">\n'
        f'    <p style="margin: 0; font-size: 15px; line-height: 1.8; color: {theme.ink}; '
        f'font-weight: 700;">{convert_inline(text, theme)}</p>\n'
        f'</section>'
    )


def render_image_placeholder(image_id: str, theme: Theme) -> str:
    if theme.is_life:
        return (
            f'<section data-fp-image-placeholder="{image_id}" data-wa-variant="life-scene" '
            f'style="margin: 40px 0 44px; padding: 0; text-align: center; box-sizing: border-box;">\n'
            f'  <p style="margin: 0 auto; font-size: 15px; line-height: 1; color: {theme.emphasis}; '
            f'font-weight: 700; letter-spacing: 0;">↓</p>\n'
            f'</section>'
        )
    return (
        f'<section data-fp-image-placeholder="{image_id}" style="margin: 38px 0 42px; padding: 0; '
        f'text-align: center; box-sizing: border-box;">\n'
        f'  <p style="margin: 0; padding: 0; color: {theme.section}; font-size: 0; line-height: 1;">'
        f'<span style="display: inline-block; width: 38%; border-top: 1px solid {theme.hairline}; '
        f'vertical-align: middle;"></span>'
        f'<span style="display: inline-block; width: 28px; height: 28px; margin: 0 9px; '
        f'border: 1px solid {theme.section}; border-radius: 2px; color: {theme.section}; '
        f'font-size: 15px; line-height: 26px; font-weight: 900; vertical-align: middle;">↓</span>'
        f'<span style="display: inline-block; width: 38%; border-top: 1px solid {theme.hairline}; '
        f'vertical-align: middle;"></span></p>\n'
        f'</section>'
    )


def render_section_title(text: str, number: int, theme: Theme) -> str:
    """Editorial chapter head: one vertical spine, a badge and restrained depth."""
    title = clean_section_title(text)
    num = f"{number:02d}"
    if theme.is_life:
        return (
            f'<section data-wa-format="section-title" data-wa-variant="life-timeline" '
            f'style="margin: 52px 0 27px; padding: 0; box-sizing: border-box;">\n'
            f'  <p style="margin: 0 0 10px; padding: 0; font-size: 15px; line-height: 1;">'
            f'<span data-wa-format="section-badge" style="display: inline-block; width: 34px; height: 34px; '
            f'line-height: 30px; text-align: center; margin-right: 11px; vertical-align: middle; '
            f'border: 1px solid {theme.section}; border-radius: 50%; box-sizing: border-box; '
            f'color: {theme.section}; font-size: 15px; font-weight: 800;">{num}</span>'
            f'<span data-wa-format="section-heading" style="display: inline; vertical-align: middle; '
            f'font-size: 15px; line-height: 1.55; color: {theme.ink}; font-weight: 850;">'
            f'{convert_inline(title, theme)}</span></p>\n'
            f'  <p style="margin: 0; padding: 0; height: 1px; font-size: 15px; line-height: 1; '
            f'border-top: 1px solid {theme.hairline};">'
            f'<span style="display: block; width: 68px; margin-top: -1px; '
            f'border-top: 2px solid {theme.subsection};">&nbsp;</span></p>\n'
            f'</section>'
        )
    number_color = (theme.section, theme.subsection, theme.emphasis, theme.tertiary)[(number - 1) % 4]
    return (
        f'<section data-wa-format="section-title" data-wa-variant="business-rail" '
        f'style="margin: 52px 0 29px; padding: 0; '
        f'border-top: 1px solid {theme.hairline}; border-bottom: 1px solid {theme.hairline}; '
        f'box-sizing: border-box;">\n'
        f'    <p style="margin: 0; padding: 13px 0; line-height: 1.5;">'
        f'<span data-wa-format="section-badge" style="display: inline-block; width: 38px; height: 28px; '
        f'line-height: 24px; text-align: center; margin-right: 12px; vertical-align: middle; '
        f'border-top: 3px solid {number_color}; border-right: 1px solid {number_color}; '
        f'border-bottom: 1px solid {number_color}; border-left: 1px solid {number_color}; '
        f'border-radius: 2px; background: transparent; '
        f'box-sizing: border-box; color: {number_color}; font-size: 15px; '
        f'font-weight: 900; letter-spacing: 0;">{num}</span>'
        f'<span data-wa-format="section-heading" style="display: inline; vertical-align: middle; '
        f'font-size: 15px; line-height: 1.45; color: {theme.ink}; font-weight: 850; '
        f'letter-spacing: 0;">{convert_inline(title, theme)}</span></p>\n'
        f'</section>'
    )


def render_breath(text: str, theme: Theme) -> str:
    """A natural one-sentence pause without turning it into a slogan card."""
    if theme.is_life:
        return (
            f'<p data-wa-format="breath" data-wa-variant="life-pause" '
            f'style="margin: 2.35em 0 2.45em; padding: 0 16px; '
            f'border-left: 1px solid {theme.section}; border-right: 1px solid {theme.subsection}; '
            f'font-size: 15px; line-height: 1.85; color: {theme.ink}; font-weight: 750; '
            f'letter-spacing: 0; text-align: center;">{convert_inline(text, theme)}</p>'
        )
    return (
        f'<p data-wa-format="breath" style="margin: 2.1em 0 2.2em; padding: 0 0 0 13px; '
        f'border-left: 2px solid {theme.tertiary}; font-size: 15px; line-height: 1.75; '
        f'color: {theme.ink}; font-weight: 700; letter-spacing: 0; text-align: left;">'
        f'{convert_inline(text, theme)}</p>'
    )


def is_breath_paragraph(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if not 4 <= len(compact) <= 34:
        return False
    sentence_ends = re.findall(r"[。！？!?…]+", compact)
    return len(sentence_ends) <= 1 and bool(
        re.match(
            r"^(?:但|可|所以|因为|问题是|真正|这不是|这意味着|换句话说|更重要的是)",
            compact,
        )
    )


def looks_like_reader_questions(lines: list[str], *, is_trailing_quote: bool = False) -> bool:
    """Detect optional closing discussion by structure: trailing quote with list items."""
    if not is_trailing_quote:
        return False
    text = "\n".join(lines).strip()
    if not text:
        return False
    item_count = len(
        re.findall(r"(?:^|\n)\s*(?:[-*]\s+|\d+[\.．、\)]\s*)\S+", text)
    )
    return item_count >= 1


def render_reader_questions(lines: list[str], theme: Theme) -> str:
    """Rounded invite card using the article-authored title and up to 3 questions."""
    cleaned_lines = [re.sub(r"^>\s?", "", line).strip() for line in lines]
    cleaned_lines = [line for line in cleaned_lines if line]
    invite_title = ""
    body_lines: list[str] = []
    for line in cleaned_lines:
        if re.match(r"^(?:[-*]\s+|\d+[\.．、\)]\s*)", line):
            body_lines.append(line)
            continue
        if not body_lines and not invite_title:
            invite_title = re.sub(r"^[*#\s]+|[*#\s]+$", "", line).strip("*").strip()
            continue
        if body_lines:
            body_lines.append(line)

    # WeChat-safe unicode markers (no external images); rotate brand colors for emphasis.
    question_icons = ("✦", "✧", "▸")
    question_colors = (theme.section, theme.subsection, theme.emphasis)

    question_rows: list[str] = []
    for line in body_lines:
        item = re.sub(r"^(?:[-*]\s+|\d+[\.．、\)]\s*)", "", line).strip()
        item = re.sub(r"^[*#\s]+|[*#\s]+$", "", item).strip("*").strip()
        if not item:
            continue
        index = len(question_rows)
        icon = question_icons[index % len(question_icons)]
        icon_color = question_colors[index % len(question_colors)]
        question_rows.append(
            f'    <p data-wa-format="reader-question" style="margin: 0 0 10px; padding: 0; '
            f'font-size: 15px; line-height: 1.65; color: {theme.ink_secondary}; text-align: left;">'
            f'<span data-wa-format="reader-q-icon" style="display: inline-block; min-width: 18px; '
            f'margin-right: 8px; color: {icon_color}; font-size: 15px; font-weight: 900; '
            f'line-height: 1.65; vertical-align: baseline;">{icon}</span>'
            f'<span style="color: {theme.muted};">{convert_inline(item, theme)}</span></p>'
        )
        if len(question_rows) >= MAX_READER_QUESTIONS:
            break
    if not question_rows:
        return ""
    last = question_rows[-1]
    question_rows[-1] = last.replace("margin: 0 0 10px;", "margin: 0;", 1)
    invite_html = (
        f'    <p data-wa-format="reader-invite" style="margin: 0 0 6px; color: {theme.subsection}; '
        f'font-size: 15px; font-weight: 900; letter-spacing: 0.5px; text-align: center;">'
        f'{convert_inline(invite_title, theme)}</p>\n'
        if invite_title
        else ""
    )
    if theme.is_life:
        return (
            f'<section data-wa-format="reader-questions" data-wa-variant="life-conversation" '
            f'style="margin: 48px 0 12px; padding: 21px 8px 17px 18px; '
            f'border-top: 1px solid {theme.section}; border-right: 0; '
            f'border-bottom: 1px solid {theme.hairline}; border-left: 2px solid {theme.subsection}; '
            f'border-radius: 0; box-sizing: border-box;">\n'
            + invite_html
            + "\n".join(question_rows)
            + "\n</section>"
        )
    return (
        f'<section data-wa-format="reader-questions" style="margin: 44px 0 10px; padding: 20px 18px 18px; '
        f'border: 1px solid {theme.border}; border-left: 4px solid {theme.subsection}; '
        f'border-radius: 8px; box-sizing: border-box;">\n'
        f'    <p data-wa-format="reader-invite-icon" style="margin: 0 0 8px; text-align: center; '
        f'font-size: 15px; line-height: 1.2; color: {theme.subsection};">'
        f'<span style="display: inline-block; padding: 4px 12px; border-radius: 999px; '
        f'background: transparent; border: 1px solid {theme.border}; '
        f'color: {theme.subsection}; font-size: 15px; line-height: 1.2;">💬</span></p>\n'
        + invite_html
        +
        f'    <p style="margin: 0 0 14px; text-align: center; font-size: 15px; line-height: 1; '
        f'color: {theme.hairline}; letter-spacing: 6px;">· · ·</p>\n'
        + "\n".join(question_rows)
        + "\n</section>"
    )


def render_punch(text: str, theme: Theme) -> str:
    if theme.is_life:
        if nonspace_len(text) <= PUNCH_MAX_CHARS:
            return (
                f'<section data-wa-format="punch" data-wa-variant="life-note" '
                f'style="margin: 30px 0; padding: 4px 0 9px 15px; '
                f'border-left: 3px solid {theme.emphasis}; border-bottom: 1px solid {theme.hairline}; '
                f'box-sizing: border-box;">\n'
                f'  <p style="margin: 0; font-size: 15px; line-height: 1.8; color: {theme.ink}; '
                f'font-weight: 850; text-align: left;">{convert_inline(text, theme)}</p>\n'
                f'</section>'
            )
        return (
            f'<section data-wa-format="punch" data-wa-variant="life-reflection" '
            f'style="margin: 35px 0; padding: 17px 12px 16px; '
            f'border-top: 1px solid {theme.section}; border-bottom: 1px solid {theme.subsection}; '
            f'box-sizing: border-box;">\n'
            f'  <p style="margin: 0; font-size: 15px; line-height: 1.85; color: {theme.ink}; '
            f'font-weight: 850; text-align: center;">{convert_inline(text, theme)}</p>\n'
            f'</section>'
        )
    if nonspace_len(text) <= PUNCH_MAX_CHARS:
        return (
            f'<section data-wa-format="punch" data-wa-variant="compact" '
            f'style="margin: 29px 0; padding: 9px 14px 10px; '
            f'border-top: 1px solid {theme.hairline}; border-right: 1px solid {theme.hairline}; '
            f'border-bottom: 1px solid {theme.hairline}; border-left: 4px solid {theme.emphasis}; '
            f'border-radius: 2px; '
            f'box-sizing: border-box;">\n'
            f'  <p style="margin: 0; font-size: 15px; line-height: 1.7; '
            f'color: {theme.ink}; font-weight: 900; letter-spacing: 0;">'
            f'<span style="display: inline-block; width: 24px; margin-right: 10px; '
            f'border-top: 3px solid {theme.emphasis}; vertical-align: 5px;">&nbsp;</span>'
            f'{convert_inline(text, theme)}</p>\n'
            f'</section>'
        )
    return (
        f'<section data-wa-format="punch" data-wa-variant="statement" '
        f'style="margin: 33px 0; padding: 16px 18px 15px; '
        f'border-top: 2px solid {theme.emphasis}; border-right: 1px solid {theme.hairline}; '
        f'border-bottom: 1px solid {theme.hairline}; border-left: 1px solid {theme.hairline}; '
        f'border-radius: 2px; '
        f'box-sizing: border-box;">\n'
        f'  <p style="margin: 0; font-size: 15px; line-height: 1.7; '
        f'color: {theme.ink}; font-weight: 900; letter-spacing: 0; text-align: center;">'
        f'{convert_inline(text, theme)}</p>\n'
        f'</section>'
    )


def highlight_code_lines(code_text: str, language: str) -> tuple[list[str], bool]:
    """Return inline-styled code lines without changing the source text."""
    plain_lines = [html.escape(line) for line in code_text.split("\n")] if code_text else [""]
    if not language or pygments_highlight is None or HtmlFormatter is None or get_lexer_by_name is None:
        return plain_lines, False

    aliases = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "sh": "bash",
        "shell": "bash",
        "yml": "yaml",
        "md": "markdown",
        "txt": "text",
        "text": "text",
        "plaintext": "text",
    }
    lexer_name = aliases.get(language.lower(), language.lower())
    try:
        lexer = get_lexer_by_name(lexer_name)
        rendered = pygments_highlight(
            code_text,
            lexer,
            HtmlFormatter(nowrap=True, noclasses=True, style="monokai"),
        ).rstrip("\n")
    except Exception:
        return plain_lines, False
    return rendered.split("\n") if rendered else [""], True


def render_code_block(lines: list[str], theme: Theme) -> str:
    language = lines[0].strip() if lines else ""
    code_text = "\n".join(lines[1:] if lines else []).rstrip("\n")
    code_text = code_text.replace("\t", "    ")
    language_label = language.upper() if language else "代码"
    escaped_language = html.escape(language_label[:24])
    code_lines, highlighted = highlight_code_lines(code_text, language)
    rendered_lines = []
    for line_number, line in enumerate(code_lines, start=1):
        escaped_line = line
        if not escaped_line:
            escaped_line = "<br>"
        rendered_lines.append(
            f'    <p data-wa-code-line="{line_number}" style="display: flex; margin: 0; padding: 0; '
            f'font-family: Menlo, Monaco, Consolas, \'Courier New\', monospace; '
            f'font-size: 15px; line-height: 1.6; color: {theme.code_ink}; text-align: left; '
            f'white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; tab-size: 4;">'
            f'<span data-wa-code-gutter="true" style="display: inline-block; width: 28px; '
            f'flex: 0 0 28px; padding-right: 10px; color: #636366; text-align: right; '
            f'user-select: none;"><span leaf="">{line_number:02d}</span></span>'
            f'<span data-wa-code-text="true" style="display: block; min-width: 0; flex: 1; '
            f'white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;">'
            f'<span leaf="" style="white-space: pre-wrap;">{escaped_line}</span></span></p>'
        )
    return (
        f'<section data-wa-format="code-block" data-wa-code-language="{html.escape(language_label[:24])}" '
        f'data-wa-code-highlight="{"pygments" if highlighted else "plain"}" '
        f'style="margin: 30px 0 34px; padding: 0; border: 1px solid {theme.code_border}; '
        f'border-left: 4px solid {theme.section}; border-radius: 12px; overflow: hidden; '
        f'background: {theme.code_background}; box-shadow: {theme.code_shadow}; box-sizing: border-box;">\n'
        f'  <section style="display: flex; align-items: center; justify-content: space-between; '
        f'margin: 0; min-height: 34px; padding: 0 14px; border-bottom: 1px solid {theme.code_border}; '
        f'background: {theme.code_header}; box-sizing: border-box;">'
        f'<span style="display: inline-block; min-width: 88px;">'
        f'<span leaf="" style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; '
        f'background: #FF5F56; margin-right: 7px; font-size: 0; line-height: 0;">.</span>'
        f'<span leaf="" style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; '
        f'background: #FFBD2E; margin-right: 7px; font-size: 0; line-height: 0;">.</span>'
        f'<span leaf="" style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; '
        f'background: #27C93F; margin-right: 12px; font-size: 0; line-height: 0;">.</span></span>'
        f'<span leaf="" style="font-family: Menlo, Monaco, Consolas, \'Courier New\', monospace; '
        f'font-size: 15px; line-height: 1.4; color: {theme.code_muted}; letter-spacing: 1px; '
        f'font-weight: 700; text-align: center;">{escaped_language}</span>'
        f'<span style="display: inline-block; min-width: 88px; text-align: right; color: #636366; '
        f'font-size: 15px; letter-spacing: 2px;"><span leaf="">•••</span></span></section>\n'
        f'  <section style="margin: 0; padding: 13px 14px 15px; box-sizing: border-box;">\n'
        + "\n".join(rendered_lines)
        + '\n  </section>\n</section>'
    )


def image_id_from_block(btype: str, lines: list[str]) -> str | None:
    if btype != "paragraph":
        return None
    text = " ".join(lines).strip()
    marker = IMAGE_MARKER_RE.fullmatch(text)
    if marker:
        return marker.group(1) or marker.group(2)
    image = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", text)
    if image:
        url = image.group(2).strip()
        return Path(url).stem if url else "image"
    return None


def organize_image_anchors(
    blocks: list[tuple[str, list[str]]],
) -> tuple[list[tuple[str, list[str]]], dict[int, list[str]]]:
    """Detach image markers and assign them to their surrounding article section.

    Stage 5 markers are structural anchors, not prose. Detaching them prevents a
    marker from sitting directly below a heading or splitting an unfinished
    sentence. Rendering later places each image after real chapter context.
    """

    clean_blocks: list[tuple[str, list[str]]] = []
    section_images: dict[int, list[str]] = {}
    section_index = 0
    title_seen = False
    continuation_open = False
    image_detached_since_block = False
    detached_image_ids: list[str] = []

    def sentence_complete(lines: list[str]) -> bool:
        text = " ".join(lines).rstrip()
        # Markdown emphasis and code markers are not sentence content. Without
        # removing them, a complete `**重点句。**` is mistaken for an unfinished
        # sentence and merged with the paragraph after an image anchor.
        text = re.sub(r"[*_`~\s]+$", "", text)
        return bool(re.search(r"[。！？!?；;…」』”’）)\]]$", text))

    def merge_continuation(previous_lines: list[str], next_lines: list[str]) -> list[str]:
        merged = list(previous_lines)
        left = merged[-1].rstrip()
        right = next_lines[0].lstrip()
        left_word = re.search(r"([A-Za-z]+)$", left)
        joins_word = bool(left_word and len(left_word.group(1)) <= 2 and re.match(r"^[A-Za-z]", right))
        joins_cjk = bool(re.search(r"[\u4e00-\u9fff]$", left) or re.match(r"^[\u4e00-\u9fff]", right))
        separator = "" if joins_word or joins_cjk else " "
        merged[-1] = left + separator + right
        merged.extend(next_lines[1:])
        return merged

    for btype, lines in blocks:
        image_id = image_id_from_block(btype, lines)
        if image_id:
            section_images.setdefault(section_index, []).append(image_id)
            image_detached_since_block = True
            detached_image_ids.append(image_id)
            if clean_blocks:
                previous_type, previous_lines = clean_blocks[-1]
                continuation_open = (
                    previous_type in {"paragraph", "quote"}
                    and not sentence_complete(previous_lines)
                )
            continue

        if btype == "heading":
            raw = lines[0].strip()
            if not title_seen:
                title_seen = True
            elif raw.startswith("## "):
                section_index += 1

        if continuation_open and clean_blocks and btype == "paragraph":
            previous_type, previous_lines = clean_blocks[-1]
            if previous_type in {"paragraph", "quote"}:
                merged_lines = merge_continuation(previous_lines, lines)
                clean_blocks[-1] = (previous_type, merged_lines)
                continuation_open = not sentence_complete(merged_lines)
                continue

        if image_detached_since_block and clean_blocks and btype == "list":
            previous_type, previous_lines = clean_blocks[-1]
            if previous_type == "list":
                previous_ordered = bool(re.match(r"^\d+\.\s+", previous_lines[0].strip()))
                current_ordered = bool(re.match(r"^\d+\.\s+", lines[0].strip()))
                if previous_ordered == current_ordered:
                    clean_blocks[-1] = ("list", [*previous_lines, *lines])
                    pending = section_images.get(section_index, [])
                    for detached_id in detached_image_ids:
                        if detached_id in pending:
                            pending.remove(detached_id)
                    clean_blocks.append(("anchored_images", list(detached_image_ids)))
                    image_detached_since_block = False
                    detached_image_ids = []
                    continuation_open = False
                    continue

        clean_blocks.append((btype, lines))
        continuation_open = False
        image_detached_since_block = False
        detached_image_ids = []

    return clean_blocks, section_images


def render_blocks(
    blocks: list[tuple[str, list[str]]],
    theme: Theme,
) -> str:
    blocks, section_images = organize_image_anchors(blocks)
    html_blocks: list[str] = []
    section_number = 0
    section_index = 0
    body_blocks_in_section = 0
    body_chars_in_section = 0
    title_rendered = False
    lead_used = False
    breath_sections: set[int] = set()
    quote_indices = [index for index, (block_type, _) in enumerate(blocks) if block_type == "quote"]
    last_quote_index = quote_indices[-1] if quote_indices else -1

    def place_section_images(force: bool = False) -> None:
        pending = section_images.get(section_index, [])
        has_context = (
            body_blocks_in_section >= IMAGE_MIN_BODY_BLOCKS
            and body_chars_in_section >= IMAGE_MIN_CONTEXT_CHARS
        )
        reached_breathing_limit = body_blocks_in_section >= IMAGE_MAX_BODY_BLOCKS
        if not pending or (not force and not has_context and not reached_breathing_limit):
            return
        html_blocks.extend(render_image_placeholder(image_id, theme) for image_id in pending)
        section_images[section_index] = []

    def note_body_block(source_text: str) -> None:
        nonlocal body_blocks_in_section, body_chars_in_section
        body_blocks_in_section += 1
        body_chars_in_section += nonspace_len(source_text)
        place_section_images()

    for block_index, (btype, lines) in enumerate(blocks):
        if btype == "anchored_images":
            html_blocks.extend(render_image_placeholder(image_id, theme) for image_id in lines)
            continue

        if btype == "heading":
            raw = lines[0].strip()
            if not title_rendered:
                title_rendered = True
                text = re.sub(r"^#+\s*", "", raw).strip()
                html_blocks.append(render_article_title(text, theme))
            elif raw.startswith("## "):
                place_section_images(force=True)
                section_index += 1
                body_blocks_in_section = 0
                body_chars_in_section = 0
                section_number += 1
                html_blocks.append(render_section_title(raw[3:].strip(), section_number, theme))
            elif raw.startswith("### "):
                html_blocks.append(render_subsection_title(raw[4:].strip(), theme))
            continue

        if btype == "code":
            html_blocks.append(render_code_block(lines, theme))
            note_body_block("\n".join(lines[1:]))
            continue

        if btype == "quote":
            if looks_like_reader_questions(
                lines, is_trailing_quote=(block_index == last_quote_index)
            ):
                questions_html = render_reader_questions(lines, theme)
                if questions_html:
                    html_blocks.append(questions_html)
                    note_body_block("\n".join(lines))
                    continue
            text = clean_quote_lead(" ".join(lines).strip())
            html_blocks.append(render_quote(text, theme))
            note_body_block(text)
            continue

        if btype == "list":
            items = []
            ordered = bool(re.match(r"^\d+\.\s+", lines[0].strip()))
            start_match = re.match(r"^(\d+)\.\s+", lines[0].strip())
            start_number = int(start_match.group(1)) if ordered and start_match else 1
            for item_offset, line in enumerate(lines):
                item_index = start_number + item_offset
                text = re.sub(r"^([\*\-\+]\s+|\d+\.\s+)", "", line.strip())
                marker_color = theme.section if item_offset % 2 == 0 else theme.subsection
                marker = (
                    f'<span style="display: inline-block; '
                    f'width: 22px; height: 22px; flex: 0 0 22px; margin: 2px 10px 0 0; '
                    f'border: 1px solid {marker_color}; border-radius: 2px; background: transparent; '
                    f'color: {marker_color}; font-size: 15px; line-height: 20px; '
                    f'text-align: center; font-weight: 800; box-sizing: border-box;">{item_index}</span>'
                    if ordered
                    else f'<span style="display: inline-block; width: 22px; flex: 0 0 22px; '
                    f'margin: 0 10px 0 0; color: {theme.section}; font-size: 15px; '
                    f'line-height: 1.4; text-align: center;">•</span>'
                )
                items.append(
                    f'<li style="display: flex; align-items: flex-start; margin: 0 0 10px; '
                    f'padding: 2px 0; color: {theme.ink_secondary}; list-style: none; line-height: 1.9;">'
                    f'{marker}<span style="display: block; flex: 1 1 auto; min-width: 0; '
                    f'font-size: 15px; line-height: 1.9; color: {theme.ink_secondary};">'
                    f'{convert_inline(text, theme)}</span></li>'
                )
            tag = "ol" if ordered else "ul"
            html_blocks.append(
                f'<{tag} data-wa-format="list" style="margin: 0 0 1.7em {"0" if ordered else "22px"}; padding: 0; '
                f'font-size: 15px; line-height: 1.9; color: {theme.subsection};">'
                + "".join(items)
                + f'</{tag}>'
            )
            note_body_block(" ".join(lines))
            continue

        if btype == "table":
            rows: list[list[str]] = []
            for line in lines:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if not parts or all(re.fullmatch(r":?-+:?", p) for p in parts):
                    continue
                rows.append(parts)
            if rows:
                table_rows = []
                for row_index, row in enumerate(rows):
                    cell_tag = "th" if row_index == 0 else "td"
                    cell_color = theme.section if row_index == 0 else theme.ink_secondary
                    cells = "".join(
                        f'<{cell_tag} style="border: 1px solid {theme.border}; padding: 9px 10px; '
                        f'color: {cell_color}; '
                        f'font-weight: {"800" if row_index == 0 else "400"}; text-align: left;">'
                        f'{convert_inline(cell, theme)}</{cell_tag}>'
                        for cell in row
                    )
                    table_rows.append(f"<tr>{cells}</tr>")
                html_blocks.append(
                    f'<section data-wa-format="table" style="margin: 22px 0 28px; overflow: hidden; '
                    f'border: 1px solid {theme.border}; border-top: 3px solid {theme.section}; '
                    f'border-radius: 2px;">'
                    f'<table style="width: 100%; border-collapse: collapse; font-size: 15px; '
                    f'line-height: 1.7;">'
                    + "".join(table_rows)
                    + "</table></section>"
                )
                note_body_block(" ".join(" ".join(row) for row in rows))
            continue

        text = " ".join(lines).strip()
        if HORIZONTAL_RULE_RE.fullmatch(text):
            continue

        if looks_like_step_subtitle(text):
            html_blocks.append(render_subsection_title(text, theme))
            continue

        if re.fullmatch(r"\*\*(?s:.+)\*\*", text):
            html_blocks.append(render_punch(text[2:-2].strip(), theme))
            note_body_block(text)
            continue

        if not lead_used and nonspace_len(text) >= 24:
            lead_used = True
            html_blocks.append(render_opening_lead(text, theme))
            note_body_block(text)
            continue

        if is_breath_paragraph(text) and section_index not in breath_sections:
            html_blocks.append(render_breath(text, theme))
            breath_sections.add(section_index)
            note_body_block(text)
            continue

        html_blocks.append(
            f'<p style="margin: 0 0 1.65em; font-size: 15px; line-height: 1.9; color: {theme.ink_secondary}; '
            f'text-align: left; letter-spacing: 0;">{convert_inline(text, theme)}</p>'
        )
        note_body_block(text)

    place_section_images(force=True)
    return "\n\n".join(html_blocks)


def write_wechat_html(topic_dir: Path, *, quiet: bool = False) -> Path:
    """Build article/final_article_copy.html from final_article.md. Returns output path."""
    topic_dir = ensure_topic_dir(topic_dir)
    md_path = topic_dir / "article" / "final_article.md"
    output_path = topic_dir / "article" / "final_article_copy.html"
    if not md_path.exists():
        fail(f"final_article.md does not exist at: {md_path}")

    accent, supporting = choose_palette(topic_dir)
    mode = article_mode(topic_dir)
    theme = Theme(accent, supporting, mode=mode)

    blocks = parse_blocks(md_path.read_text(encoding="utf-8"))
    # The first substantive paragraph becomes the opening-lead card.
    body_html = render_blocks(blocks, theme)

    full_html = (
        '<meta charset="UTF-8">\n'
        f'<section data-wa-theme="{mode.replace("_", "-")}" '
        f'style="max-width: 640px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, '
        f"'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif; "
        f"font-size: 15px; line-height: 1.9; color: {theme.ink_secondary}; word-wrap: break-word; "
        f'text-align: left; padding: 8px 16px 28px; box-sizing: border-box;">\n'
        f"{body_html}\n"
        "</section>\n"
    )

    try:
        output_path.write_text(full_html, encoding="utf-8")
    except OSError as exc:
        fail(
            f"Cannot write {output_path}: {exc}. "
            "Topic dirs outside the repo need a shell with full filesystem write access."
        )
    if not quiet:
        print(f"Successfully generated WeChat paste-safe HTML at: {output_path}")
        print(
            json.dumps(
                {
                    "palette": {
                    "ink": theme.ink,
                    "mode": mode,
                    "section": theme.section,
                        "subsection": theme.subsection,
                        "emphasis": theme.emphasis,
                        "tertiary": theme.tertiary,
                    }
                },
                ensure_ascii=False,
            )
        )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert final_article.md to WeChat paste-safe HTML.")
    parser.add_argument("--topic-dir", help="Path to topic folder containing article/final_article.md")
    args = parser.parse_args()
    write_wechat_html(resolve_topic_dir(args.topic_dir))


if __name__ == "__main__":
    main()
