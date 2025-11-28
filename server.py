import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.getenv("PORT", "10000"))

def start_bot():
    subprocess.Popen([sys.executable, "bot.py"])

def run_server():
    server = ThreadingHTTPServer(("", PORT), SimpleHTTPRequestHandler)
    print(f"Servidor online na porta {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    start_bot()
    run_server()