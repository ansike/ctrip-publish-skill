#!/usr/bin/env python3
"""
携程笔记发布 MCP Server
使用 Model Context Protocol 与 OpenClaw 通信
支持 Cookie 持久化，保存 vbkticket 实现登录态复用
"""

import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Cookie 存储路径
COOKIE_DIR = Path.home() / ".config" / "ctrip-publish"
COOKIE_FILE = COOKIE_DIR / "cookies.json"

class CtripCookieManager:
    """携程 Cookie 管理器 - 持久化登录态"""
    
    def __init__(self):
        self.cookies = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        COOKIE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """从文件加载 cookies"""
        if COOKIE_FILE.exists():
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cookies: {e}", file=sys.stderr)
                self.cookies = {}
    
    def save(self):
        """保存 cookies 到文件"""
        try:
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cookies, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save cookies: {e}", file=sys.stderr)
            return False
    
    def get(self, name: str) -> Optional[str]:
        """获取指定 cookie"""
        return self.cookies.get(name)
    
    def set(self, name: str, value: str, domain: str = "we.ctrip.com"):
        """设置 cookie"""
        self.cookies[name] = {
            "value": value,
            "domain": domain,
            "path": "/"
        }
        self.save()
    
    def get_vbkticket(self) -> Optional[str]:
        """获取 vbkticket（携程登录态关键 cookie）"""
        vbk = self.cookies.get("vbkticket")
        if isinstance(vbk, dict):
            return vbk.get("value")
        return vbk
    
    def set_vbkticket(self, value: str):
        """设置 vbkticket"""
        self.set("vbkticket", value, "we.ctrip.com")
    
    def get_all_cookies_dict(self) -> Dict[str, str]:
        """获取所有 cookie 为简单字典格式"""
        result = {}
        for name, data in self.cookies.items():
            if isinstance(data, dict):
                result[name] = data.get("value", "")
            else:
                result[name] = str(data)
        return result
    
    def is_logged_in(self) -> bool:
        """检查是否已登录（有 vbkticket）"""
        return self.get_vbkticket() is not None
    
    def clear(self):
        """清除所有 cookies"""
        self.cookies = {}
        if COOKIE_FILE.exists():
            COOKIE_FILE.unlink()


class CtripMCPServer:
    """携程发布 MCP Server"""
    
    def __init__(self):
        self.cookie_manager = CtripCookieManager()
        self.tools = {
            "search_images": self.search_images,
            "download_images": self.download_images,
            "fill_form": self.fill_form,
            "upload_images": self.upload_images,
            "publish": self.publish,
            "get_cookies": self.get_cookies,
            "set_cookie": self.set_cookie,
            "check_login": self.check_login,
            "clear_cookies": self.clear_cookies,
        }
    
    def run(self):
        """主循环 - 读取 stdin 的 JSON-RPC 请求"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                if response:
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                    
            except json.JSONDecodeError:
                self.send_error(None, -32700, "Parse error")
            except Exception as e:
                self.send_error(None, -32603, f"Internal error: {str(e)}")
    
    def handle_request(self, request: Dict) -> Optional[Dict]:
        """处理 JSON-RPC 请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "ctrip-publish-mcp",
                        "version": "3.4.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return self._get_tools_list(request_id)
        
        elif method == "tools/call":
            return self._call_tool(request_id, params)
        
        return None
    
    def _get_tools_list(self, request_id) -> Dict:
        """获取工具列表"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "search_images",
                        "description": "从 Bing Images 搜索高清图片",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "keyword": {
                                    "type": "string",
                                    "description": "搜索关键词，如 '故宫'、'长城'"
                                },
                                "count": {
                                    "type": "integer",
                                    "description": "搜索数量",
                                    "default": 5
                                }
                            },
                            "required": ["keyword"]
                        }
                    },
                    {
                        "name": "download_images",
                        "description": "下载图片到本地",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "urls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "图片URL列表"
                                },
                                "output_dir": {
                                    "type": "string",
                                    "description": "输出目录",
                                    "default": "/tmp/openclaw/uploads"
                                }
                            },
                            "required": ["urls"]
                        }
                    },
                    {
                        "name": "fill_form",
                        "description": "填写携程发布表单",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "标题（必须少于20字）"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "正文内容"
                                },
                                "destination": {
                                    "type": "string",
                                    "description": "目的地，如 '北京'",
                                    "default": ""
                                },
                                "date": {
                                    "type": "string",
                                    "description": "日期，如 '2026-04-04'",
                                    "default": ""
                                }
                            },
                            "required": ["title", "content"]
                        }
                    },
                    {
                        "name": "upload_images",
                        "description": "上传图片到携程页面",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "image_paths": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "图片文件路径列表"
                                },
                                "cdp_url": {
                                    "type": "string",
                                    "description": "CDP WebSocket URL"
                                }
                            },
                            "required": ["image_paths", "cdp_url"]
                        }
                    },
                    {
                        "name": "publish",
                        "description": "点击发布按钮",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "cdp_url": {
                                    "type": "string",
                                    "description": "CDP WebSocket URL"
                                }
                            },
                            "required": ["cdp_url"]
                        }
                    },
                    {
                        "name": "get_cookies",
                        "description": "获取保存的 cookies（包括 vbkticket）",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "set_cookie",
                        "description": "设置 cookie 并持久化保存",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "cookie 名称"
                                },
                                "value": {
                                    "type": "string",
                                    "description": "cookie 值"
                                },
                                "domain": {
                                    "type": "string",
                                    "description": "cookie 域",
                                    "default": "we.ctrip.com"
                                }
                            },
                            "required": ["name", "value"]
                        }
                    },
                    {
                        "name": "check_login",
                        "description": "检查是否已登录（是否有 vbkticket）",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "clear_cookies",
                        "description": "清除所有保存的 cookies",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    
    def _call_tool(self, request_id, params: Dict) -> Dict:
        """调用工具"""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        if tool_name in self.tools:
            try:
                result = self.tools[tool_name](**tool_params)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": f"Tool execution error: {str(e)}"
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    def search_images(self, keyword: str, count: int = 5) -> Dict:
        """搜索图片"""
        return {
            "status": "success",
            "message": f"搜索关键词: {keyword}",
            "instruction": "使用 browser 工具访问 Bing Images 搜索",
            "url": f"https://cn.bing.com/images/search?q={keyword.replace(' ', '+')}+1920x1080",
            "expected_results": count
        }
    
    def download_images(self, urls: List[str], output_dir: str = "/tmp/openclaw/uploads") -> Dict:
        """下载图片"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        instructions = []
        for i, url in enumerate(urls, 1):
            instructions.append(f"curl -L '{url}' -o {output_dir}/{i}.jpg")
        
        return {
            "status": "success",
            "message": f"准备下载 {len(urls)} 张图片",
            "output_dir": output_dir,
            "instructions": instructions,
            "note": "使用 exec 工具执行 curl 命令下载图片"
        }
    
    def fill_form(self, title: str, content: str, destination: str = "", date: str = "") -> Dict:
        """填写表单"""
        # 验证标题长度
        if len(title) >= 20:
            return {
                "status": "error",
                "message": f"标题超长: {len(title)}字，必须少于20字",
                "suggestion": "请缩短标题到19字以内"
            }
        
        # 验证正文字数
        if len(content) < 60:
            return {
                "status": "warning",
                "message": f"正文仅{len(content)}字，建议≥60字以评为优质"
            }
        
        return {
            "status": "success",
            "message": "表单内容已准备好",
            "title": title,
            "title_length": len(title),
            "content_length": len(content),
            "destination": destination,
            "date": date or "2026-04-04",
            "instructions": [
                "1. 使用 browser 工具打开 https://we.ctrip.com/publish/publishPictureText",
                "2. 使用 act + evaluate 填写标题",
                "3. 使用 act + evaluate 填写正文",
                "4. 使用 act + evaluate 选择目的地"
            ]
        }
    
    def upload_images(self, image_paths: List[str], cdp_url: str) -> Dict:
        """上传图片"""
        return {
            "status": "success",
            "message": f"准备上传 {len(image_paths)} 张图片",
            "cdp_url": cdp_url,
            "image_paths": image_paths,
            "instructions": [
                "使用 Python + websockets 连接 CDP",
                "调用 DOM.setFileInputFiles 上传图片"
            ],
            "python_code": f"""
import json, asyncio, websockets

async def upload():
    async with websockets.connect('{cdp_url}') as ws:
        # 获取DOM
        await ws.send(json.dumps({{"id": 1, "method": "DOM.getDocument", "params": {{"depth": -1}}}}))
        doc = json.loads(await ws.recv())
        
        # 查找file input
        await ws.send(json.dumps({{
            "id": 2,
            "method": "DOM.querySelector",
            "params": {{"nodeId": doc["result"]["root"]["nodeId"], "selector": "input[type='file']"}}
        }}))
        q = json.loads(await ws.recv())
        
        # 上传文件
        await ws.send(json.dumps({{
            "id": 3,
            "method": "DOM.setFileInputFiles",
            "params": {{"nodeId": q["result"]["nodeId"], "files": {image_paths}}}
        }}))
        
asyncio.run(upload())
"""
        }
    
    def publish(self, cdp_url: str) -> Dict:
        """发布"""
        return {
            "status": "success",
            "message": "准备点击发布按钮",
            "cdp_url": cdp_url,
            "instructions": [
                "使用 browser act + evaluate 点击发布按钮",
                "检查页面是否跳转到详情页（包含 articleId）"
            ],
            "javascript": """
const publishBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText?.trim() === '发 布');
if(publishBtn) {
    publishBtn.click();
    return 'clicked';
}
return 'not found';
"""
        }
    
    # ========== Cookie 管理工具 ==========
    
    def get_cookies(self) -> Dict:
        """获取所有 cookies"""
        cookies = self.cookie_manager.get_all_cookies_dict()
        vbk = self.cookie_manager.get_vbkticket()
        
        return {
            "status": "success",
            "cookies": cookies,
            "vbkticket": vbk,
            "is_logged_in": self.cookie_manager.is_logged_in(),
            "cookie_file": str(COOKIE_FILE),
            "note": "vbkticket 是携程登录态的关键 cookie"
        }
    
    def set_cookie(self, name: str, value: str, domain: str = "we.ctrip.com") -> Dict:
        """设置 cookie"""
        self.cookie_manager.set(name, value, domain)
        
        return {
            "status": "success",
            "message": f"Cookie '{name}' 已保存",
            "name": name,
            "domain": domain,
            "cookie_file": str(COOKIE_FILE)
        }
    
    def check_login(self) -> Dict:
        """检查登录状态"""
        is_logged_in = self.cookie_manager.is_logged_in()
        vbk = self.cookie_manager.get_vbkticket()
        
        return {
            "status": "success",
            "is_logged_in": is_logged_in,
            "has_vbkticket": vbk is not None,
            "vbkticket_preview": vbk[:20] + "..." if vbk and len(vbk) > 20 else vbk,
            "message": "已登录" if is_logged_in else "未登录，需要重新扫码",
            "cookie_file": str(COOKIE_FILE)
        }
    
    def clear_cookies(self) -> Dict:
        """清除 cookies"""
        self.cookie_manager.clear()
        
        return {
            "status": "success",
            "message": "所有 cookies 已清除",
            "cookie_file": str(COOKIE_FILE)
        }
    
    def send_error(self, request_id, code: int, message: str):
        """发送错误响应"""
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    server = CtripMCPServer()
    server.run()
    
    def run(self):
        """主循环 - 读取 stdin 的 JSON-RPC 请求"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                if response:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                self.send_error(None, -32700, "Parse error")
            except Exception as e:
                self.send_error(None, -32603, f"Internal error: {str(e)}")
    
    def handle_request(self, request: Dict) -> Optional[Dict]:
        """处理 JSON-RPC 请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "ctrip-publish-mcp",
                        "version": "3.3.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "search_images",
                            "description": "从 Bing Images 搜索高清图片",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "keyword": {
                                        "type": "string",
                                        "description": "搜索关键词，如 '故宫'、'长城'"
                                    },
                                    "count": {
                                        "type": "integer",
                                        "description": "搜索数量",
                                        "default": 5
                                    }
                                },
                                "required": ["keyword"]
                            }
                        },
                        {
                            "name": "download_images",
                            "description": "下载图片到本地",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "图片URL列表"
                                    },
                                    "output_dir": {
                                        "type": "string",
                                        "description": "输出目录",
                                        "default": "/tmp/openclaw/uploads"
                                    }
                                },
                                "required": ["urls"]
                            }
                        },
                        {
                            "name": "fill_form",
                            "description": "填写携程发布表单",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "标题（必须少于20字）"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "正文内容"
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "目的地，如 '北京'",
                                        "default": ""
                                    },
                                    "date": {
                                        "type": "string",
                                        "description": "日期，如 '2026-04-04'",
                                        "default": ""
                                    }
                                },
                                "required": ["title", "content"]
                            }
                        },
                        {
                            "name": "upload_images",
                            "description": "上传图片到携程页面",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "image_paths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "图片文件路径列表"
                                    },
                                    "cdp_url": {
                                        "type": "string",
                                        "description": "CDP WebSocket URL"
                                    }
                                },
                                "required": ["image_paths", "cdp_url"]
                            }
                        },
                        {
                            "name": "publish",
                            "description": "点击发布按钮",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "cdp_url": {
                                        "type": "string",
                                        "description": "CDP WebSocket URL"
                                    }
                                },
                                "required": ["cdp_url"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**tool_params)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": f"Tool execution error: {str(e)}"
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        return None
    
    def search_images(self, keyword: str, count: int = 5) -> Dict:
        """搜索图片"""
        return {
            "status": "success",
            "message": f"搜索关键词: {keyword}",
            "instruction": "使用 browser 工具访问 Bing Images 搜索",
            "url": f"https://cn.bing.com/images/search?q={keyword.replace(' ', '+')}+1920x1080",
            "expected_results": count
        }
    
    def download_images(self, urls: List[str], output_dir: str = "/tmp/openclaw/uploads") -> Dict:
        """下载图片"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        instructions = []
        for i, url in enumerate(urls, 1):
            instructions.append(f"curl -L '{url}' -o {output_dir}/{i}.jpg")
        
        return {
            "status": "success",
            "message": f"准备下载 {len(urls)} 张图片",
            "output_dir": output_dir,
            "instructions": instructions,
            "note": "使用 exec 工具执行 curl 命令下载图片"
        }
    
    def fill_form(self, title: str, content: str, destination: str = "", date: str = "") -> Dict:
        """填写表单"""
        # 验证标题长度
        if len(title) >= 20:
            return {
                "status": "error",
                "message": f"标题超长: {len(title)}字，必须少于20字",
                "suggestion": "请缩短标题到19字以内"
            }
        
        # 验证正文字数
        if len(content) < 60:
            return {
                "status": "warning",
                "message": f"正文仅{len(content)}字，建议≥60字以评为优质"
            }
        
        return {
            "status": "success",
            "message": "表单内容已准备好",
            "title": title,
            "title_length": len(title),
            "content_length": len(content),
            "destination": destination,
            "date": date or "2026-04-04",
            "instructions": [
                "1. 使用 browser 工具打开 https://we.ctrip.com/publish/publishPictureText",
                "2. 使用 act + evaluate 填写标题",
                "3. 使用 act + evaluate 填写正文",
                "4. 使用 act + evaluate 选择目的地"
            ]
        }
    
    def upload_images(self, image_paths: List[str], cdp_url: str) -> Dict:
        """上传图片"""
        return {
            "status": "success",
            "message": f"准备上传 {len(image_paths)} 张图片",
            "cdp_url": cdp_url,
            "image_paths": image_paths,
            "instructions": [
                "使用 Python + websockets 连接 CDP",
                "调用 DOM.setFileInputFiles 上传图片"
            ],
            "python_code": f"""
import json, asyncio, websockets

async def upload():
    async with websockets.connect('{cdp_url}') as ws:
        # 获取DOM
        await ws.send(json.dumps({{"id": 1, "method": "DOM.getDocument", "params": {{"depth": -1}}}}))
        doc = json.loads(await ws.recv())
        
        # 查找file input
        await ws.send(json.dumps({{
            "id": 2,
            "method": "DOM.querySelector",
            "params": {{"nodeId": doc["result"]["root"]["nodeId"], "selector": "input[type='file']"}}
        }}))
        q = json.loads(await ws.recv())
        
        # 上传文件
        await ws.send(json.dumps({{
            "id": 3,
            "method": "DOM.setFileInputFiles",
            "params": {{"nodeId": q["result"]["nodeId"], "files": {image_paths}}}
        }}))
        
asyncio.run(upload())
"""
        }
    
    def publish(self, cdp_url: str) -> Dict:
        """发布"""
        return {
            "status": "success",
            "message": "准备点击发布按钮",
            "cdp_url": cdp_url,
            "instructions": [
                "使用 browser act + evaluate 点击发布按钮",
                "检查页面是否跳转到详情页（包含 articleId）"
            ],
            "javascript": """
const publishBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText?.trim() === '发 布');
if(publishBtn) {
    publishBtn.click();
    return 'clicked';
}
return 'not found';
"""
        }
    
    def send_error(self, request_id, code: int, message: str):
        """发送错误响应"""
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message}
        }), flush=True)

if __name__ == "__main__":
    server = CtripMCPServer()
    server.run()