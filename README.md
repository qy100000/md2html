# md2html

将单个 Markdown 文件转换为**带样式、自包含**的 HTML 文件。

输出的 HTML 内嵌全部 CSS（GitHub 风格正文样式 + Pygments 代码高亮），无任何外部依赖，可直接分享、用浏览器打开或邮件发送。

## 特性

- **单文件转换**： `md2html.py input.md` 一条命令完成
- **完整 Markdown 语法**： 表格、围栏代码块、脚注、内嵌HTML、列表、引用等（Python-Markdown `extra` 全家桶）
- **代码高亮**： Pygments 服务端着色，支持 ```` ```python ```` 等语言标注
- **中文友好**： 中文标题锚点（Unicode slugify）、中文字体优先（Microsoft YaHei / 苹方）
- **自包含产物**： CSS 全内嵌，无 CDN / 外部 JS 依赖，离线可用
- **智能标题**： `<title>` 自动取文档第一个 `# 标题`，否则用文件名
- **UTF-8 全链路**： 读入容错 BOM，输出带 `<meta charset="utf-8">`

## 环境要求

- Python 3.8+
- 依赖安装：

```bash
pip install markdown pygments
```

## 使用方法

```cmd
# 基本用法: 生成 input.html (同目录同名)
python md2html.py input.md

# 指定输出路径
python md2html.py input.md -o out.html
```

## HTML 特性一览

| 特性 | 扩展/实现 |
|------|-----------|
| 表格（含对齐） | `extra` → `tables` |
| 围栏代码块 + 着色 | `extra` → `fenced_code` + `codehilite` + Pygments |
| 标题锚点 id | `toc` + `slugify_unicode` |
| 脚注 | `extra` → `footnotes` |
| 内嵌 HTML | `extra` → `md_in_html` |
| GitHub 风格样式 | 内嵌 CSS（标题/表格斑马纹/引用块/行内代码等） |

## 示例

仓库内的 `test_sample.md` 是一个覆盖常用语法的测试样例：

```cmd
python md2html.py test_sample.md
# → 生成 test_sample.html
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `md2html.py` | 主程序（单文件） |
| `test_sample.md` | 测试样例（标题/表格/多语言代码块/引用/脚注） |
| `requirements.txt` | 依赖清单 |

## License

MIT
