---
name: 携程笔记全自动发布
version: 3.1.0
description: 携程内容中心全自动发布技能，支持从 Bing Images 搜索高清无版权图片、自动填写标题正文、自动上传图片、自动选择目的地、自动点击发布。适用于旅行攻略、美食推荐等图文笔记发布。
emoji: 🚄
---

# 携程笔记全自动发布技能

## 功能

- ✅ 自动打开携程发布页面
- ✅ 自动从 Bing Images 搜索高清无版权图片
- ✅ 自动填写标题和正文（支持 Markdown 格式）
- ✅ 自动上传图片（最多20张）
- ✅ 自动选择目的地
- ✅ 自动设置拍摄时间
- ✅ 自动添加话题标签
- ✅ 自动点击发布

## 使用场景

当用户说：
- "发携程笔记"
- "发布到携程"
- "全自动发布携程笔记"
- "帮我发到携程"
- "写一篇携程攻略"

## 技术实现

使用 OpenClaw 浏览器自动化 + CDP 协议：
1. 通过浏览器 CDP 连接页面
2. 导航到携程内容中心发布页面
3. 自动填写表单字段（标题、正文、地点）
4. 使用 CDP setFileInputFiles 上传图片
5. 自动点击发布按钮
6. 处理发布确认弹窗

## 图片搜索功能

内置 Bing Images 搜索，可根据关键词自动下载高清图：
- 故宫、天坛、长城、胡同、鸟巢等北京景点
- 自动过滤低分辨率图片
- 优先选择 1920x1080 以上的高清图

## 依赖

- OpenClaw 浏览器工具
- Python 3 + websockets (用于 CDP)
- 网络访问 Bing Images

## 配置

无需 API Key，但需要：
1. 登录携程账号（首次需要扫码）
2. 图片上传到 /tmp/openclaw/uploads/

## 页面元素定位

### 携程发布页面关键元素

```
页面URL: https://we.ctrip.com/publish/publishPictureText

关键选择器:
- 图片上传: input[type="file"]
- 标题输入: [role="textbox"] (第一个)
- 正文编辑器: [role="combobox"] (第一个)
- 地点选择: .ant-select-selection-search-input
- 日期选择: input[placeholder*="日期"]
- 发布按钮: button:has-text("发 布")
- 存草稿: button:has-text("存草稿")
```

### 成功判断

- 发布成功后 URL 包含 `detail?articleId=`
- 或页面跳转到内容详情页

## 使用示例

用户：帮我发一篇北京3天2晚的攻略到携程

AI：
1. 自动打开携程发布页面
2. 搜索下载北京相关高清图片
3. 填写标题："北京3天2晚攻略！人均1500元玩转帝都"
4. 填写正文行程内容
5. 自动选择目的地为"北京"
6. 自动上传图片
7. 点击发布

## 注意事项

1. 首次使用需要用户登录携程账号
2. 图片数量建议 3-20 张
3. 标题建议 5-20 字
4. 正文建议 60 字以上（更容易被评为优质）
5. 热门景点需提前预约（如故宫）
6. 发布后需等待审核

## 快速链接

- 图文发布：https://we.ctrip.com/publish/publishPictureText
- 创作者后台：https://we.ctrip.com/publish/publishHome
- 内容管理：https://we.ctrip.com/publish/contentManagement