import psutil
import subprocess
import platform

# --- FERRAMENTAS DE LEITURA ---

def obter_info_sistema() -> str:
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return (
            f"Sistema: {platform.system()} {platform.release()}\n"
            f"CPU: {psutil.cpu_count()} núcleos, Uso: {cpu_percent}%\n"
            f"RAM: Total {mem.total // (1024**3)}GB, Disponível {mem.available // (1024**3)}GB, Uso: {mem.percent}%\n"
            f"Disco: Total {disk.total // (1024**3)}GB, Livre {disk.free // (1024**3)}GB, Uso: {disk.percent}%\n"
        )
    except Exception as e:
        return f"Erro ao obter informações do sistema: {e}"

def testar_conectividade(host: str) -> str:
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '4', host], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return f"Ping para {host} bem-sucedido. O host está acessível.\nSaída:\n{result.stdout[:500]}..."
        else:
            return f"Ping para {host} falhou. O host pode estar inacessível.\nErro:\n{result.stderr[:500]}..."
    except subprocess.TimeoutExpired:
        return f"Ping para {host} excedeu o tempo limite (10s)."
    except Exception as e:
        return f"Erro ao executar o ping: {e}"

def listar_processos_pesados() -> str:
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        top_cpu = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:5]
        top_ram = sorted(processes, key=lambda p: p['memory_percent'] or 0, reverse=True)[:5]
        res_cpu = "Top 5 Processos por CPU:\n" + "\n".join([f"- {p['name']} (PID {p['pid']}): {p['cpu_percent']}%" for p in top_cpu])
        res_ram = "Top 5 Processos por RAM:\n" + "\n".join([f"- {p['name']} (PID {p['pid']}): {p['memory_percent']:.1f}%" for p in top_ram])
        return f"{res_cpu}\n\n{res_ram}"
    except Exception as e:
        return f"Erro ao listar processos: {e}"

def verificar_servicos_windows() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    servicos = ["Spooler", "Dnscache", "Dhcp"]
    resultado = "Estado dos Serviços Críticos:\n"
    for servico in servicos:
        try:
            out = subprocess.run(['sc', 'query', servico], capture_output=True, text=True)
            if "RUNNING" in out.stdout: resultado += f"- {servico}: A correr (OK)\n"
            elif "STOPPED" in out.stdout: resultado += f"- {servico}: Parado (Atenção!)\n"
            else: resultado += f"- {servico}: Não encontrado.\n"
        except Exception as e: resultado += f"- {servico}: Erro ({e})\n"
    return resultado

def verificar_portas_abertas() -> str:
    try:
        connections = psutil.net_connections(kind='inet')
        listening_ports = set()
        for conn in connections:
            if conn.status == 'LISTEN':
                listening_ports.add(f"- Porta {conn.laddr.port} (IP: {conn.laddr.ip})")
        if not listening_ports: return "Nenhuma porta em estado LISTEN encontrada."
        return "Portas em escuta (LISTEN):\n" + "\n".join(sorted(list(listening_ports))[:15]) + "\n(Mostrando apenas as primeiras 15)"
    except Exception as e:
        return f"Erro ao verificar portas: {e}"

# --- FERRAMENTAS DE AÇÃO (ESCRITA) ---

def limpar_cache_dns() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    try:
        result = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
        return "Cache de DNS limpa com sucesso!" if result.returncode == 0 else f"Erro: {result.stderr}"
    except Exception as e: return f"Erro ao executar comando: {e}"

def reiniciar_spooler() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    try:
        subprocess.run(['net', 'stop', 'spooler'], capture_output=True, text=True)
        subprocess.run(['net', 'start', 'spooler'], capture_output=True, text=True)
        return "Serviço de Impressão (Spooler) reiniciado com sucesso!"
    except Exception as e:
        return f"Erro ao reiniciar o spooler (pode necessitar de permissões de Administrador): {e}"

def renovar_ip() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    try:
        subprocess.run(['ipconfig', '/release'], capture_output=True, text=True)
        subprocess.run(['ipconfig', '/renew'], capture_output=True, text=True)
        return "IP renovado com sucesso! O computador pediu um novo endereço IP ao servidor DHCP."
    except Exception as e:
        return f"Erro ao renovar o IP: {e}"

def reiniciar_placa_rede() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    try:
        # Reinicia o adaptador de rede principal (Wi-Fi ou Ethernet)
        subprocess.run(['powershell', '-Command', 'Restart-NetAdapter -Name * -Confirm:$false'], capture_output=True, text=True)
        return "Placa de rede reiniciada com sucesso!"
    except Exception as e:
        return f"Erro ao reiniciar a placa de rede: {e}"

def executar_sfc_scannow() -> str:
    if platform.system().lower() != 'windows': return "Só disponível em Windows."
    try:
        # Nota: Este comando demora alguns minutos. O backend vai ficar bloqueado à espera.
        result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True)
        if "did not find any integrity violations" in result.stdout:
            return "A verificação do sistema (SFC) terminou e não encontrou ficheiros corrompidos."
        return "A verificação do sistema (SFC) terminou. Verifica o terminal do Windows para ver os detalhes."
    except Exception as e:
        return f"Erro ao executar o SFC (pode necessitar de permissões de Administrador): {e}"

# Lista de ferramentas de LEITURA
TOOLS_LIST = [
    obter_info_sistema, testar_conectividade, listar_processos_pesados,
    verificar_servicos_windows, verificar_portas_abertas
]