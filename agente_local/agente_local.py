import asyncio
import websockets
import json
import subprocess
import platform
import uuid

# ⚠️ SUBSTITUI PELO URL DO TEU RENDER (SEM O HTTP, USA WS)
# Exemplo: wss://agente-suporte-ti-backend.onrender.com/ws/agente
RENDER_WS_URL = "https://agente-suporte-ti-backend.onrender.com"

def executar_comando(acao):
    """Executa o comando no Windows e devolve o resultado."""
    print(f"⚙️ Executando: {acao}...")
    try:
        if acao == "diagnosticar_impressao":
            res_spooler = subprocess.run(['sc', 'query', 'Spooler'], capture_output=True, text=True)
            spooler_status = "RUNNING" if "RUNNING" in res_spooler.stdout else "STOPPED"
            res_fila = subprocess.run(['powershell', '-Command', 'Get-PrintJob | Measure-Object | Select-Object -ExpandProperty Count'], capture_output=True, text=True)
            num_jobs = int(res_fila.stdout.strip() or 0)
            return {"status": "success", "spooler": spooler_status, "fila_presa": num_jobs}

        elif acao == "diagnosticar_rede":
            res_dns = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True, timeout=5)
            dns_ok = res_dns.returncode == 0 and "Non-existent" not in res_dns.stdout
            return {"status": "success", "dns_ok": dns_ok}

        elif acao == "corrigir_spooler":
            subprocess.run(['powershell', '-Command', 'Get-PrintJob | Remove-PrintJob -Confirm:$false'], capture_output=True)
            subprocess.run(['net', 'stop', 'spooler'], capture_output=True)
            subprocess.run(['net', 'start', 'spooler'], capture_output=True)
            return {"status": "success", "message": "Serviço de impressão reiniciado e fila limpa!"}

        elif acao == "limpar_dns":
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            return {"status": "success", "message": "Cache de DNS limpa com sucesso!"}

        return {"status": "error", "message": "Ação desconhecida."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def conectar():
    while True:
        try:
            print(f"🔗 A tentar ligar ao servidor: {RENDER_WS_URL}...")
            async with websockets.connect(RENDER_WS_URL) as websocket:
                print("✅ LIGADO AO RENDER! À espera de comandos do Agente...")
                
                async for mensagem in websocket:
                    data = json.loads(mensagem)
                    req_id = data.get("id")
                    acao = data.get("acao")
                    
                    # Executa o comando
                    resultado = executar_comando(acao)
                    
                    # Devolve a resposta ao Render com o mesmo ID
                    resposta = {"id": req_id, "resultado": resultado}
                    await websocket.send(json.dumps(resposta))
                    print(f"📤 Resposta enviada para o Render.")
                    
        except websockets.exceptions.ConnectionClosed:
            print("❌ Ligação perdida. A tentar reconectar em 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Erro: {e}. A tentar reconectar em 5 segundos...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("=========================================")
    print(" AGENTE DE SUPORTE TI - WEBSOCKET CLIENT")
    print("=========================================")
    asyncio.run(conectar())