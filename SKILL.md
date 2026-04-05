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

### ✨ 优质笔记特征（被评为优质的共同点）

#### 1. 标题特点
- ✅ 使用 emoji（如 🏨🏯🎨🛏️🚌🔑🎡🍽️🏞️❤️）
- ✅ 突出关键词（地点/景点/店名）
- ✅ 引起好奇（"顶流"、"百年奢华"、"小众好逛"）

**优质标题示例**：
```
住进紫禁城旁的百年奢华✨躺着看故宫🏨（18字）
北京旅游｜3天2夜全攻略，直接抄作业📝（16字）
模式口驼铃古道徒步，看法海寺壁画💯（14字）
```

#### 2. 内容结构（推荐模板）

```
【开头】抓住注意力
推开窗就是故宫角楼鎏金屋顶，这才是京城顶流酒店该有的排面！🏯

【正文章节】使用 emoji + 【】方括号分区
🏨【介绍】民宿/酒店整体介绍
【民宿地址】具体地址
🎨【装修风格】装修特点
🛏️【房型/布局】房间详情
🚌【交通攻略】地铁/自驾/步行路线
🔑【入住方式】入住提示
🎡【游玩项目】设施服务
🍽️【餐厅特色】餐饮信息
🏞️【周边景点】附近景点
❤️【tips】实用小贴士

【结尾】互动引导
#话题标签1 #话题标签2 #话题标签3
```

#### 3. 内容要点
- ✅ 包含具体实用信息（地址、电话、交通、价格）
- ✅ 使用 emoji 分隔章节
- ✅ 使用【】方括号标注章节名
- ✅ 结尾有互动引导（"找TA聊聊"）
- ✅ 2-5个相关话题标签

#### 4. 字数
- 建议 **500-1500字**

#### 5. 图片
- ✅ 高清、与内容相关
- ✅ 3-20张
- ✅ 无水印

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

### list_articles 获取笔记列表
```python
list_articles(quality_only=True, limit=50)
# 返回: { "totalCount": 70, "articles": [...] }
```

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
## 📋 正确的工作流程

### 正确顺序（重要！）

1. **先确定主题** - 写标题和正文内容
2. **根据内容关键词找图片** - 从正文中提取关键词，搜索对应图片
3. **上传图片** - 上传与内容相关的图片
4. **选择地点** - 填入目的地
5. **发布**

### 错误顺序（避免）

❌ 先上传图片，再写内容
❌ 先选地点，再写内容

### 内容关键词提取示例

正文包含以下景点：
- 天安门、故宫 → 搜索"天安门故宫"
- 长城 → 搜索"北京长城"
- 鸟巢、水立方 → 搜索"北京鸟巢"
- 南锣鼓巷、什刹海 → 搜索"北京胡同"

根据内容中的关键词搜索对应的高清图片，确保图片与内容相关。
