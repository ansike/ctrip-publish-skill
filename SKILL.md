---
name: ctrip-publish-mcp
version: 3.3.0
description: 携程笔记全自动发布 MCP Server - 支持搜索图片、填写内容、上传图片、发布笔记
emoji: 🚄
---

# 携程笔记发布 MCP Server

这是一个基于 **Model Context Protocol (MCP)** 的携程笔记发布工具。

## 架构

```
OpenClaw <-> MCP Server (stdio) <-> 浏览器 CDP
```

## 提供的 Tools

### 1. search_images
搜索高清图片

**参数:**
- `keyword` (string): 搜索关键词，如 "故宫"、"长城"
- `count` (integer): 搜索数量，默认 5

**返回:** Bing Images 搜索 URL

### 2. download_images
下载图片到本地

**参数:**
- `urls` (array): 图片URL列表
- `output_dir` (string): 输出目录，默认 `/tmp/openclaw/uploads`

### 3. fill_form
填写发布表单

**参数:**
- `title` (string): 标题（必须少于20字）
- `content` (string): 正文内容
- `destination` (string): 目的地，如 "北京"
- `date` (string): 日期，如 "2026-04-04"

**验证:**
- 标题长度 < 20 字
- 正文长度 ≥ 60 字（建议）

### 4. upload_images
上传图片到携程页面

**参数:**
- `image_paths` (array): 图片文件路径列表
- `cdp_url` (string): CDP WebSocket URL

### 5. publish
点击发布按钮

**参数:**
- `cdp_url` (string): CDP WebSocket URL

## 使用流程

```
1. search_images(keyword="故宫") 
   -> 获取 Bing Images URL
   
2. browser.navigate(url)
   -> 打开图片搜索页面
   
3. download_images(urls=[...])
   -> 下载图片到本地
   
4. fill_form(title="...", content="...")
   -> 验证内容格式
   
5. browser.navigate(url="https://we.ctrip.com/publish/publishPictureText")
   -> 打开发布页面
   
6. browser.act(kind="evaluate", fn="...")
   -> 填写标题、正文
   
7. upload_images(image_paths=[...], cdp_url="...")
   -> 上传图片
   
8. publish(cdp_url="...")
   -> 点击发布
```

## 配置

`_meta.json`:
```json
{
  "name": "ctrip-publish-mcp",
  "version": "3.3.0",
  "runtime": "mcp",
  "mcp": {
    "type": "stdio",
    "command": "python3",
    "args": ["server.py"]
  }
}
```

## 依赖

- Python 3.8+
- websockets (用于 CDP 连接)

## GitHub

https://github.com/ansike/ctrip-publish-skill