import http.server
import socketserver
import json
import subprocess
import urllib.parse

PORT = 5050

class AgentHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "os": "Windows"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        action = data.get("action")
        result = {"status": "error", "message": "Ação desconhecida."}

        if action == "diagnosticar_impressao":
            try:
                res_spooler = subprocess.run(['sc', 'query', 'Spooler'], capture_output=True, text=True)
                spooler_status = "RUNNING" if "RUNNING" in res_spooler.stdout else "STOPPED"
                res_fila = subprocess.run(['powershell', '-Command', 'Get-PrintJob | Measure-Object | Select-Object -ExpandProperty Count'], capture_output=True, text=True)
                num_jobs = int(res_fila.stdout.strip() or 0)
                result = {"status": "success", "spooler": spooler_status, "fila_presa": num_jobs}
            except Exception as e:
                result = {"status": "error", "message": str(e)}

        elif action == "diagnosticar_rede":
            try:
                res_dns = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True, timeout=5)
                dns_ok = res_dns.returncode == 0 and "Non-existent" not in res_dns.stdout
                result = {"status": "success", "dns_ok": dns_ok}
            except Exception:
                result = {"status": "success", "dns_ok": False}

        elif action == "corrigir_spooler":
            try:
                subprocess.run(['powershell', '-Command', 'Get-PrintJob | Remove-PrintJob -Confirm:$false'], capture_output=True)
                subprocess.run(['net', 'stop', 'spooler'], capture_output=True)
                subprocess.run(['net', 'start', 'spooler'], capture_output=True)
                result = {"status": "success", "message": "Serviço de impressão reiniciado e fila limpa!"}
            except Exception as e:
                result = {"status": "error", "message": str(e)}

        elif action == "limpar_dns":
            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
                result = {"status": "success", "message": "Cache de DNS limpa com sucesso!"}
            except Exception as e:
                result = {"status": "error", "message": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

with socketserver.TCPServer(("", PORT), AgentHandler) as httpd:
    print("=========================================")
    print(" AGENTE DE SUPORTE TI - ONLINE")
    print("=========================================")
    print(f"A escutar na porta {PORT}...")
    print("Mantém esta janela aberta.")
    httpd.serve_forever()