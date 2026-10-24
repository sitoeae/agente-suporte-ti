import subprocess
import platform
import json

def diagnosticar_rede() -> str:
    """Executa um diagnóstico de rede focado em DNS e IP."""
    if platform.system().lower() != 'windows':
        return "Erro: Só disponível em Windows."

    # 1. Testar DNS
    try:
        dns_test = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True, timeout=5)
        if dns_test.returncode != 0 or "Non-existent domain" in dns_test.stdout or "server can't find" in dns_test.stdout:
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": "O DNS não está a conseguir resolver nomes (ex: google.com).",
                "acao_sugerida": "LIMPAR_DNS",
                "confianca": 0.95
            })
    except subprocess.TimeoutExpired:
        return json.dumps({
            "status": "PROBLEMA_ENCONTRADO",
            "causa_provavel": "O servidor DNS não respondeu a tempo (Timeout).",
            "acao_sugerida": "LIMPAR_DNS",
            "confianca": 0.90
        })
    except Exception:
        pass

    # 2. Verificar IP e Gateway
    try:
        ipconfig = subprocess.run(['ipconfig'], capture_output=True, text=True)
        if "Media disconnected" in ipconfig.stdout:
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": "O cabo de rede está desligado ou o Wi-Fi está desativado.",
                "acao_sugerida": "REINICIAR_REDE",
                "confianca": 0.99
            })
        if "169.254" in ipconfig.stdout:
            return json.dumps({
                "status": "PROBLEMA_ENCONTRADO",
                "causa_provavel": "O computador não conseguiu obter um IP do servidor DHCP (APIPA).",
                "acao_sugerida": "RENOVAR_IP",
                "confianca": 0.95
            })
    except Exception:
        pass

    return json.dumps({
        "status": "SEM_PROBLEMAS_CLAROS",
        "causa_provavel": "A rede parece funcional (DNS resolve, IP atribuído).",
        "acao_sugerida": "NENHUMA"
    })

def corrigir_dns() -> str:
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
        subprocess.run(['ipconfig', '/registerdns'], capture_output=True, text=True)
        return "Cache de DNS limpa e registos renovados!"
    except Exception as e: return f"Erro: {e}"

def corrigir_ip() -> str:
    try:
        subprocess.run(['ipconfig', '/release'], capture_output=True, text=True)
        subprocess.run(['ipconfig', '/renew'], capture_output=True, text=True)
        return "IP renovado com sucesso!"
    except Exception as e: return f"Erro: {e}"

def reiniciar_rede() -> str:
    try:
        subprocess.run(['powershell', '-Command', 'Restart-NetAdapter -Name * -Confirm:$false'], capture_output=True, text=True)
        return "Placa de rede reiniciada!"
    except Exception as e: return f"Erro: {e}"