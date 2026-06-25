#!/usr/bin/env python3
"""
ETF数据分析 HTTP 服务器
使用: python3 server.py [端口]

启动后浏览器访问:
  http://localhost:8080/全量指数申购流入排行.html

数据更新后刷新浏览器即可, 无需重启服务器。
"""
import subprocess, sys

port = sys.argv[1] if len(sys.argv) > 1 else "8080"
print(f"🚀 ETF分析服务器已启动")
print(f"   地址: http://localhost:{port}/全量指数申购流入排行.html")
print(f"   数据: etf_history/etf_data.json (由 gen_analysis_html.py 生成)")
print(f"   提示: 数据更新后刷新浏览器即可")
print(f"   按 Ctrl+C 停止\n")
subprocess.run([sys.executable, "-m", "http.server", port, "--directory",
                "/Users/andy/WorkBuddy/2026-06-24-23-34-24"])
