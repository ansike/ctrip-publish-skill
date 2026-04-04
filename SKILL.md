---
name: ctrip-publish-mcp
version: 1.0.1
description: 携程笔记全自动发布 MCP Server - 支持 Cookie 持久化(vbkticket)、搜索图片、填写内容、上传图片、发布笔记
emoji: 🚄
---

# 携程笔记发布 MCP Server

基于 **Model Context Protocol (MCP)** 的携程笔记发布工具，支持登录态持久化。

## ⚠️ 注意事项（必读）

### 📝 内容限制

| 字段 | 限制 | 说明 |
|------|------|------|
| 标题 | **<20字** | 不能是≤20字，必须少于！ |
| 正文 | ≥60字 | 建议60字以上，容易被评为优质 |
| 图片 | 3-20张 | ≥3张有机会评为优质 |

**错误示例**：
- ❌ 标题："北京3天2晚攻略！人均1500元玩转帝都" (21字 - 超长)
- ✅ 标题："北京3天攻略！人均1500玩转帝都" (17字)

### 🖼️ 图片要求

- **高清**：建议 1920×1080 以上
- **无水印**：关闭水印开关
- **无版权**：使用 Bing Images 搜索的无版权图
- **关联性**：图片要与内容相关

### 📍 地点选择

- 必须正确选择目的地（如"北京·中国"）
- 有时需要多次点击才能选中

### 🔐 登录态

- Cookie 持久化在 `~/.config/ctrip-publish/cookies.json`
- 关键 cookie：`vbkticket`
- 需要先登录一次，后续可复用

### ⏰ 发布后

- 需要等待审核
- 热门景点（故宫等）需提前7天预约

### ⚠️ 常见错误

1. **标题超长** → 报"标题字数需少于20个字"
2. **地点未选** → 发布按钮无反应
3. **正文为空** → 报"描述为必填项"

## 🛠️ 提供的 Tools

| Tool | 描述 |
|------|------|
| `search_images` | 从 Bing Images 搜索高清图片 |
| `download_images` | 下载图片到本地 |
| `fill_form` | 填写发布表单（带验证） |
| `upload_images` | 上传图片到携程页面 |
| `publish` | 点击发布按钮 |
| `get_cookies` | 获取保存的 cookies |
| `set_cookie` | 设置并保存 cookie |
| `check_login` | 检查登录状态 |
| `clear_cookies` | 清除所有 cookies |

## 使用流程

### 1. 检查登录状态
```
check_login()
-> 返回: is_logged_in, has_vbkticket
```

### 2. 如果未登录
- 使用 browser 工具打开携程登录页
- 用户扫码/密码登录
- 使用 set_cookie 保存 vbkticket

### 3. 发布笔记
```
1. search_images(keyword="故宫")
2. download_images(urls=[...])
3. fill_form(title="...", content="...")
4. upload_images(image_paths=[...], cdp_url="...")
5. publish(cdp_url="...")
```

## Cookie 管理

### 获取 vbkticket
```python
get_cookies()
# 返回: { "vbkticket": "xxx", "is_logged_in": true }
```

### 设置 vbkticket
```python
set_cookie(name="vbkticket", value="your_token", domain="we.ctrip.com")
```

### 检查登录
```python
check_login()
# 返回: { "is_logged_in": true, "has_vbkticket": true }
```

## 配置

`_meta.json`:
```json
{
  "name": "ctrip-publish-mcp",
  "version": "1.0.1",
  "runtime": "mcp",
  "mcp": {
    "type": "stdio",
    "command": "python3",
    "args": ["server.py"]
  }
}
```

## GitHub

https://github.com/ansike/ctrip-publish-skill