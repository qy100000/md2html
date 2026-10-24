# 测试文档 md2html

这是一个用于验证转换效果的 Markdown 样例，支持**粗体**、*斜体*、`行内代码`、[链接](https://www.python.org) 以及 ~~删除线~~。

## 列表测试

1. 甲骨文服务器
2. 虚拟主机
    - 嵌套项目 A
    - 嵌套项目 B
3. CDN 加速

## 表格测试

| 指标 | 数值 | 备注 |
|:-----|-----:|:----:|
| 胜率 | 72.5% | 截面口径 |
| 均笔收益 | +5.96% | — |
| 盈亏比 | 3.86 | — |

## 代码块测试（Python）

```python
def read_day_file(code):
    market = "sh" if code.startswith("6") else "sz"
    path = f"C:\\new_tdx\\vipdoc\\{market}\\lday\\{market}{code}.day"
    with open(path, "rb") as f:
        return f.read(32)  # 32 字节 / 条
```

### 无语言代码块

```
plain text 不会被 pygments 误高亮
```

### JSON 代码块

```json
{"name": "沪深300", "code": "000300", "win_rate": 0.725}
```

## 引用测试

> 高 BBW 卖点后反弹概率高，可考虑留仓吃反弹。
> —— 2026-08-30 研究结论

---

## 脚注与多级标题

这是一个脚注引用[^1]。

[^1]: 这是脚注内容。

### 三级标题
#### 四级标题
**结束。**
