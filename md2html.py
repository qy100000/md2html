#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2html — 将单个 Markdown 文件转换为带样式的 HTML 文件

用法:
    python md2html.py input.md              # 输出同目录同名 .html
    python md2html.py input.md -o out.html  # 指定输出路径

依赖:
    pip install markdown pygments   (语法解析 + 代码高亮)

特性:
    - 内嵌 CSS (GitHub 风格) 与 Pygments 高亮样式, 产物为完全自包含单文件
    - 扩展: tables / fenced_code / toc(标题锚点) / footnotes / md_in_html 等
    - <title> 自动取文档第一个 "# 标题", 否则用文件名
"""

import argparse
import io
import os
import re
import sys

try:
    import markdown
    from markdown.extensions.toc import slugify_unicode  # 中文标题锚点支持
except ImportError:
    print("错误: 缺少 markdown 库, 请先运行: pip install markdown")
    sys.exit(1)

try:
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

MARKDOWN_EXTENSIONS = [
    "extra",        # 含 tables / fenced_code / footnotes / md_in_html / attr_list 等
    "sane_lists",
    "toc",          # 为标题生成锚点 id
    "codehilite",   # Pygments 服务端代码高亮
]

CODEHILITE_CONFIG = {
    "codehilite": {
        "guess_lang": False,   # 不猜测语言, 避免纯文本被误高亮
        "noclasses": False,
    },
    "toc": {
        "slugify": slugify_unicode,  # 默认slugify会把中文标题id清成 _1/_2, 换Unicode版保留中文
    },
}

# ---------------------------------------------------------------- CSS 模板 ---

CSS_TEMPLATE = """/* ---- 基础布局 ---- */
body {
    max-width: 920px;
    margin: 40px auto;
    padding: 0 24px;
    color: #1f2328;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", sans-serif;
    font-size: 16px;
    line-height: 1.7;
    word-wrap: break-word;
}

/* ---- 标题 ---- */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.3;
    margin-top: 1.6em;
    margin-bottom: 0.7em;
}
h1 { font-size: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.05em; }
h5 { font-size: 0.95em; }
h6 { font-size: 0.9em; color: #59636e; }

/* ---- 段落与链接 ---- */
p { margin: 0.8em 0; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ---- 列表 / 引用 / 分隔线 ---- */
ul, ol { padding-left: 2em; margin: 0.8em 0; }
li { margin: 0.25em 0; }
blockquote {
    margin: 1em 0;
    padding: 0.3em 1em;
    color: #59636e;
    border-left: 4px solid #d1d9e0;
    background: #f6f8fa;
    border-radius: 0 6px 6px 0;
}
blockquote p { margin: 0.4em 0; }
hr {
    border: none;
    border-top: 2px solid #d1d9e0;
    margin: 2em 0;
}

/* ---- 行内代码 ---- */
code {
    font-family: Consolas, "JetBrains Mono", Menlo, monospace;
    font-size: 87%;
    padding: 0.18em 0.38em;
    background: #eff1f3;
    border-radius: 5px;
}

/* ---- 代码块 (codehilite) ---- */
.codehilite {
    background: #f6f8fa;
    border: 1px solid #d1d9e0;
    border-radius: 8px;
    padding: 12px 16px;
    overflow: auto;
    line-height: 1.5;
    margin: 1em 0;
}
.codehilite pre { margin: 0; }
.codehilite code {
    padding: 0;
    background: none;
    font-size: 87%;
}
/* 无语言且未走高亮的裸 pre */
pre {
    background: #f6f8fa;
    border: 1px solid #d1d9e0;
    border-radius: 8px;
    padding: 12px 16px;
    overflow: auto;
}
pre code { background: none; padding: 0; }

/* ---- 表格 ---- */
table {
    border-collapse: collapse;
    margin: 1em 0;
    width: auto;
    max-width: 100%;
    display: block;
    overflow: auto;
}
th, td {
    border: 1px solid #d1d9e0;
    padding: 6px 13px;
    text-align: left;
    vertical-align: top;
}
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(2n) td { background: #f6f8fa; }

/* ---- 图片 ---- */
img { max-width: 100%; }

/* ---- 锚点悬停链接 ---- */
.md-anchor { opacity: 0; margin-left: 6px; color: #0969da; text-decoration: none; }
h1:hover > .md-anchor, h2:hover > .md-anchor,
h3:hover > .md-anchor, h4:hover > .md-anchor,
h5:hover > .md-anchor, h6:hover > .md-anchor { opacity: 1; }
"""


def build_discussion_anchor_css() -> str:
    """占位: 保留将来可能扩展的自定义样式入口"""
    return ""


def build_html(title: str, body: str) -> str:
    """组装最终 HTML 文档"""
    parts = [
        "<!DOCTYPE html>\n",
        '<html lang="zh-CN">\n',
        "<head>\n",
        '<meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        "<title>", title, "</title>\n",
        "<style>\n",
        CSS_TEMPLATE,
        build_discussion_anchor_css(),
        "\n",
    ]
    if HAS_PYGMENTS:
        parts.append("/* ---- Pygments 高亮 ---- */\n")
        parts.append(HtmlFormatter(style="default").get_style_defs(".codehilite"))
        parts.append("\n")
    parts += [
        "</style>\n",
        "</head>\n",
        "<body>\n",
        body,
        "\n</body>\n",
        "</html>\n",
    ]
    return "".join(parts)


def extract_title(text: str, fallback: str) -> str:
    """取第一个 ATX 一级标题作为 <title>, 否则回退文件名"""
    m = re.search(r"^[ \t]{0,3}#\s+(.+?)[ \t]*#*[ \t]*$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback


def convert(in_path: str, out_path: str) -> None:
    with open(in_path, "r", encoding="utf-8-sig") as f:  # 容错 BOM
        text = f.read()

    body = markdown.markdown(
        text,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=CODEHILITE_CONFIG,
        output_format="html5",
    )
    title = extract_title(text, os.path.splitext(os.path.basename(in_path))[0])
    html = build_html(title, body)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"已生成: {out_path}  ({size_kb:.1f} KB)")


def main() -> None:
    # 防 cmd GBK 控制台崩溃 (与项目既有惯例一致)
    enc = sys.stdout.encoding or ""
    if enc.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="将单个 Markdown 文件转换为带样式的 HTML"
    )
    parser.add_argument("input", help="输入 .md 文件路径")
    parser.add_argument(
        "-o", "--output", default=None,
        help="输出 .html 路径 (默认: 输入同目录同名 .html)",
    )
    args = parser.parse_args()

    in_path = os.path.abspath(args.input)
    if not os.path.isfile(in_path):
        print(f"错误: 找不到输入文件: {in_path}")
        sys.exit(1)

    if args.output:
        out_path = os.path.abspath(args.output)
    else:
        base = os.path.splitext(in_path)[0]
        out_path = base + ".html"

    # 输出目录不存在则报错退出
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        print(f"错误: 输出目录不存在: {out_dir}")
        sys.exit(1)

    try:
        convert(in_path, out_path)
    except UnicodeDecodeError:
        print("错误: 文件不是有效的 UTF-8 编码, 请先转码 (记事本另存为 UTF-8)")
        sys.exit(1)


if __name__ == "__main__":
    main()
