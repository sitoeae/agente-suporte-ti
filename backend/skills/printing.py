import subprocess
import platform
import json

def diagnosticar_impressao() -> str:
    """
    Executa um diagnóstico completo de impressão e devolve um relatório estruturado.
    """
    if platform.system().lower() != 'windows':
        return "Erro: Esta skill só está disponível em Windows."

    relatorio = []
    
    # 1. Verificar o Serviço (Spooler)
    try:
        servico = subprocess.run(['sc', 'query', 'Spooler'], capture_output=True, text=True)
        if "STOPPED" in servico.stdout:
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": "O serviço de impressão (Spooler) está parado.",
                "acao_sugerida": "REINICIAR_SPOOLER",
                "confianca": 0.99
            })
    except Exception as e:
        relatorio.append(f"Erro ao ler serviço: {e}")

    # 2. Verificar impressoras instaladas
    try:
        cmd_impressoras = 'Get-Printer | Select-Object Name, PrinterStatus | ConvertTo-Json'
        impressoras_res = subprocess.run(['powershell', '-Command', cmd_impressoras], capture_output=True, text=True)
        
        if not impressoras_res.stdout.strip():
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": "Não existe nenhuma impressora instalada no sistema.",
                "acao_sugerida": "NENHUMA",
                "nota": "O técnico deve instalar o driver da impressora manualmente."
            })
            
        try:
            impressoras = json.loads(impressoras_res.stdout)
            if isinstance(impressoras, dict):
                impressoras = [impressoras]
            
            # Verificar se alguma está offline
            offline = [imp['Name'] for imp in impressoras if imp.get('PrinterStatus') in [0, 6]] # 0=Offline, 6=Error
            
            if offline:
                relatorio.append(f"Impressoras offline/erro: {', '.join(offline)}")
                return json.dumps({
                    "status": "PROBLEMA_ENCONTRADO",
                    "causa_provavel": f"A(s) impressora(s) {', '.join(offline)} está(ão) offline ou com erro.",
                    "acao_sugerida": "REINICIAR_SPOOLER",
                    "confianca": 0.85
                })
            
            # Se chegou aqui, as impressoras existem e parecem online
            relatorio.append(f"Impressoras detetadas e online: {', '.join([imp['Name'] for imp in impressoras])}")
            
        except json.JSONDecodeError:
            relatorio.append("Impressoras detetadas, mas não foi possível ler o estado JSON.")

    except Exception as e:
         relatorio.append(f"Erro ao ler impressoras: {e}")

    # 3. Verificar a fila de impressão
    try:
        cmd_fila = 'Get-PrintJob | Measure-Object | Select-Object -ExpandProperty Count'
        fila_res = subprocess.run(['powershell', '-Command', cmd_fila], capture_output=True, text=True)
        num_jobs = int(fila_res.stdout.strip() or 0)
        
        if num_jobs > 0:
            relatorio.append(f"Existem {num_jobs} documentos presos na fila de impressão.")
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": f"A fila de impressão está bloqueada com {num_jobs} documentos.",
                "acao_sugerida": "REINICIAR_SPOOLER",
                "confianca": 0.90
            })
    except Exception:
        pass # Ignora erros se não houver fila

    # 4. Se não encontrou problemas
    return json.dumps({
        "status": "SEM_PROBLEMAS_CLAROS",
        "causa_provavel": "O sistema de impressão parece normal (Serviço a correr, Impressoras online, Fila vazia).",
        "acao_sugerida": "NENHUMA",
        "nota": "O problema pode ser físico (cabo, papel, tinta) ou na rede da impressora."
    })

# --- REMEDIAÇÃO ---
def corrigir_spooler() -> str:
    """Limpa a fila e reinicia o Spooler."""
    try:
        # Limpar fila
        subprocess.run(['powershell', '-Command', 'Get-PrintJob | Remove-PrintJob -Confirm:$false'], capture_output=True, text=True)
        # Reiniciar serviço
        subprocess.run(['net', 'stop', 'spooler'], capture_output=True, text=True)
        subprocess.run(['net', 'start', 'spooler'], capture_output=True, text=True)
        return "Serviço de impressão reiniciado e fila limpa com sucesso!"
    except Exception as e:
        return f"Erro ao corrigir a impressão: {e}"