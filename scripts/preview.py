#!/usr/bin/env python3
"""Render profile/README.md into a GitHub-like local preview.

Rewrites the raw.githubusercontent asset URLs to local relative paths so the
page works offline, and wraps the result in GitHub's light/dark surface colors.
Output: build/preview.html (gitignored, not part of the deliverable).

Run: python3 scripts/preview.py
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/VersinoPsiOmega/.github/main/profile/"

SHELL = """<!doctype html>
<meta charset="utf-8">
<title>Preview — VersinoPsiOmega org profile</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ background:#0d1117; color:#e6edf3; margin:0; padding:32px 16px;
         font:16px/1.6 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  .wrap {{ max-width:1012px; margin:0 auto; background:#0d1117;
           border:1px solid #30363d; border-radius:6px; padding:32px 40px; }}
  img {{ max-width:100%; }}
  h2 {{ border-bottom:1px solid #21262d; padding-bottom:.3em; margin-top:28px;
        font-size:1.5em; }}
  pre {{ background:#161b22; border-radius:6px; padding:16px; overflow-x:auto;
         font:12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  code {{ font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  :not(pre) > code {{ background:#6e768166; padding:.2em .4em; border-radius:6px;
                      font-size:85%; }}
  table {{ border-collapse:collapse; display:block; overflow-x:auto; }}
  th, td {{ border:1px solid #30363d; padding:6px 13px; }}
  tr:nth-child(2n) {{ background:#161b22; }}
  a {{ color:#4493f8; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  sub {{ color:#9198a1; }}
</style>
<div class="wrap">
{body}
</div>
"""


def main():
    md = (ROOT / "profile" / "README.md").read_text(encoding="utf-8")
    md = md.replace(RAW, "")  # ".../profile/assets/x.svg" -> "assets/x.svg"
    # <picture> sources are stripped by the markdown pass; keep only the <img>
    md = re.sub(r"<source[^>]*>\s*", "", md)
    body = markdown.markdown(md, extensions=["fenced_code", "tables", "md_in_html"])
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    target = out / "preview.html"
    target.write_text(SHELL.format(body=body), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
