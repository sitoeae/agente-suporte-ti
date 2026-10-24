import psutil
import subprocess
import platform

def obter_info_sistema() -> str:
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return f"Sistema: {platform.system()} {platform.release()}\nCPU: {cpu}% | RAM: {mem.percent}% ({mem.available // (1024**3)}GB livres) | Disco: {disk.percent}% ({disk.free // (1024**3)}GB livres)\n"
    except Exception as e: return f"Erro: {e}"

def testar_conectividade(host: str) -> str:
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '4', host], capture_output=True, text=True, timeout=10)
        return f"Ping para {host}: {'OK' if result.returncode == 0 else 'Falhou'}"
    except Exception as e: return f"Erro: {e}"

def listar_processos_pesados() -> str:
    try:
        procs = [p.info for p in psutil.process_iter(['name', 'cpu_percent']) if p.info['cpu_percent']]
        top = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:3]
        return "Top 3 Processos (CPU):\n" + "\n".join([f"- {p['name']}: {p['cpu_percent']}%" for p in top])
    except Exception as e: return f"Erro: {e}"

# Ferramentas para a IA
TOOLS_LIST = [obter_info_sistema, testar_conectividade, listar_processos_pesados]