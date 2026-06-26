#!/usr/bin/env python3
"""
ETF数据分析 HTTP 服务器 — 支持静态文件 + 自选API
使用: python3 server.py [端口]

API端点:
  GET  /api/watchlist   → 返回 watchlist.json 内容
  POST /api/watchlist   → 写入 watchlist.json

启动后访问: http://localhost:8080/全量指数申购流入排行.html
"""
import http.server, socketserver, json, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DIR = os.path.dirname(os.path.abspath(__file__))
WATCH_FILE = os.path.join(DIR, "etf_history", "watchlist.json")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/watchlist':
            self._serve_watchlist()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/watchlist':
            self._save_watchlist()
        else:
            self.send_error(404)

    def _serve_watchlist(self):
        data = []
        if os.path.exists(WATCH_FILE):
            try:
                with open(WATCH_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        self._json_response(data)

    def _save_watchlist(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            if not isinstance(data, list):
                raise ValueError("must be array")
            os.makedirs(os.path.dirname(WATCH_FILE), exist_ok=True)
            with open(WATCH_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._json_response({"status": "ok", "count": len(data)})
        except Exception as e:
            self._json_response({"status": "error", "msg": str(e)}, 400)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    print(f"🚀 ETF分析服务器已启动")
    print(f"   地址: http://localhost:{PORT}/全量指数申购流入排行.html")
    print(f"   API: http://localhost:{PORT}/api/watchlist")
    print(f"   目录: {DIR}")
    print(f"   按 Ctrl+C 停止\n")

    # 初始化watchlist.json
    if not os.path.exists(WATCH_FILE):
        os.makedirs(os.path.dirname(WATCH_FILE), exist_ok=True)
        with open(WATCH_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
