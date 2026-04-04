---
name: ctrip-publish-mcp
version: 3.4.0
description: 携程笔记全自动发布 MCP Server - 支持 Cookie 持久化(vbkticket)、搜索图片、填写内容、上传图片、发布笔记
emoji: 🚄
---

# 携程笔记发布 MCP Server

基于 **Model Context Protocol (MCP)** 的携程笔记发布工具，支持登录态持久化。

## 核心特性

### 🔐 Cookie 持久化
- 自动保存 `vbkticket` 等登录态 cookie
- 存储路径：`~/.config/ctrip-publish/cookies.json`
- 一次登录，多次复用

### 🛠️ 提供的 Tools

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
  "version": "3.4.0",
  "runtime": "mcp",
  "mcp": {
    "type": "stdio",
    "command": "python3",
    "args": ["server.py"]
  }
}
```

## 重要限制

- 标题字数：**必须少于20字**（不是≤20字）
- 正文字数：建议 **≥60字** 以评为优质
- 图片数量：**3-20张**

## GitHub

https://github.com/ansike/ctrip-publish-skill