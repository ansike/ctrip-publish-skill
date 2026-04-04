---
name: 携程笔记全自动发布
version: 3.3.0
description: 携程内容中心全自动发布技能，使用 OpenClaw 浏览器工具完成发布。支持搜索高清图片、自动填写内容、上传图片、发布笔记。
emoji: 🚄
---

# 携程笔记全自动发布技能

## 功能

- ✅ 从 Bing Images 搜索高清无版权图片
- ✅ 自动填写标题和正文
- ✅ 自动上传图片
- ✅ 自动选择目的地
- ✅ 自动点击发布

## 使用场景

当用户说：
- "发携程笔记"
- "发布到携程"
- "帮我发到携程"
- "写一篇携程攻略"

## 使用方法

### 方式1：全自动流程

用户：帮我发一篇北京3天2晚的攻略到携程

AI 会自动：
1. 从 Bing Images 搜索北京景点高清图片
2. 下载故宫、长城、天坛等图片到本地
3. 打开携程发布页面
4. 填写标题（<20字）
5. 填写正文行程内容
6. 上传图片
7. 选择目的地
8. 点击发布

### 方式2：分步操作

用户也可以分步指导：
- "先帮我搜索北京图片"
- "然后填写标题和正文"
- "最后发布"

## 技术实现

使用 OpenClaw 内置浏览器工具：
- `browser` 工具：页面导航、元素操作
- `exec` 工具：Python + CDP 上传图片
- `web_search` 工具：搜索高清图片

**不使用 AppleScript 或系统脚本**，完全通过 OpenClaw 安全沙箱执行。

## 页面元素定位

```
页面URL: https://we.ctrip.com/publish/publishPictureText

关键选择器:
- 图片上传: input[type="file"] (通过 CDP setFileInputFiles)
- 标题输入: [role="textbox"] (第一个)
- 正文编辑器: [role="combobox"] (第一个)
- 地点选择: .ant-select-selection-search-input
- 发布按钮: button (innerText = "发 布")
```

## 图片搜索

使用 Bing Images 搜索关键词：
- `beijing forbidden city high resolution`
- `great wall of china 1920x1080`
- `temple of heaven beijing`
- `beijing hutong traditional`

自动过滤选择 1920x1080 以上的高清图。

## 重要限制

1. **标题字数：必须少于20字**（不是≤20字）
2. **正文字数：建议 ≥60 字**（更容易被评为优质）
3. **图片数量：3-20 张**
4. **地点选择**：必须正确选择才能发布

## 示例标题

- ✅ "北京3天攻略！人均1500玩转帝都" (17字)
- ✅ "第一次来北京必打卡的9个地方" (16字)
- ❌ "北京3天2晚攻略！人均1500元玩转帝都" (21字 - 超长)

## 示例正文结构

```
📍目的地：北京
⏰建议游玩：3天2晚
💰人均预算：1500元

Day 1 故宫+景山
故宫门票60元，提前7天预约
景山公园俯瞰全景

Day 2 长城+鸟巢
八达岭长城877路直达
鸟巢夜景免费

Day 3 胡同+天坛
南锣鼓巷文创小店
天坛门票15元

🍜 必吃美食
北京烤鸭、炸酱面、豆汁焦圈

#北京旅游 #北京攻略
```

## 常见问题

**Q: 地点选择失败怎么办？**
A: 需要手动点击地点输入框，输入"北京"，选择"北京·中国"。

**Q: 发布按钮无反应？**
A: 检查是否有必填项未填，特别是地点是否正确选择。

**Q: 图片上传失败？**
A: 确认图片路径正确，格式为 JPG/PNG，单张 <10MB。

## 快速链接

- 图文发布：https://we.ctrip.com/publish/publishPictureText
- 创作者后台：https://we.ctrip.com/publish/publishHome
- 内容管理：https://we.ctrip.com/publish/contentManagement

## GitHub

源码：https://github.com/ansike/ctrip-publish-skill