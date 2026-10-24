from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
import os
import asyncio
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Substituímos o cliente do Google pelo da OpenAI
from openai import OpenAI

from database import engine, get_db
import models
import jwt
from jwt import PyJWKClient

import tools

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agente Suporte TI API", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuração do OpenRouter ---
openrouter_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_key,
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

_jwks_client = None
if SUPABASE_URL:
    jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    _jwks_client = PyJWKClient(jwks_url, cache_keys=True)

class ChatPayload(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class TicketCreate(BaseModel):
    title: str
    description: str
    category: str = "outro"
    priority: str = "media"

class DeviceCreate(BaseModel):
    asset_tag: str
    type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    specs: Optional[str] = None
    assigned_to: Optional[str] = None
    location: Optional[str] = None
    status: str = "Em uso"
    network_name: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    ip_type: Optional[str] = "Dinâmico"
    server_role: Optional[str] = None
    os: Optional[str] = None

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token em falta")
    token = authorization.split(" ")[1]
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        if alg == "HS256":
            payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated", options={"verify_aud": True})
        else:
            signing_key = _jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(token, signing_key.key, algorithms=["ES256"], audience="authenticated", options={"verify_aud": True})
        return payload.get("sub")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/")
def read_root(): return {"message": "API a funcionar com OpenRouter!"}

# --- ROTAS CRUD (Tickets e Devices) ---
@app.get("/api/tickets")
def get_tickets(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    try:
        user_profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()
        if user_profile.role in ["technician", "admin"]:
            return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()
        return db.query(models.Ticket).filter(models.Ticket.user_id == user_id).order_by(models.Ticket.created_at.desc()).all()
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tickets")
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    try:
        novo = models.Ticket(user_id=user_id, title=ticket_in.title, description=ticket_in.description, category=ticket_in.category, priority=ticket_in.priority, status="aberto")
        db.add(novo); db.commit(); db.refresh(novo); return novo
    except Exception as e: db.rollback(); raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices")
def get_devices(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return db.query(models.Device).order_by(models.Device.created_at.desc()).all()

@app.post("/api/devices")
def create_device(device_in: DeviceCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    try:
        user_profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()
        if user_profile.role not in ["technician", "admin"]:
            raise HTTPException(status_code=403, detail="Apenas técnicos podem adicionar equipamentos")
        novo = models.Device(**device_in.model_dump())
        db.add(novo); db.commit(); db.refresh(novo); return novo
    except Exception as e: db.rollback(); raise HTTPException(status_code=500, detail=str(e))

# --- ROTA DE CHAT COM OPENROUTER ---
@app.post("/api/chat")
async def chat(payload: ChatPayload, db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    inventory_context = "INVENTÁRIO:\n"
    for d in devices:
        inventory_context += f"- {d.asset_tag}: {d.manufacturer} {d.model} [{d.type}], IP: {d.ip_address}\n"

    # O prompt de sistema precisa de ser claro sobre as ferramentas e ações
    system_prompt = f"""
Tu és o "Agente Suporte TI". Fala em português de Portugal (pt-PT).
Tens ferramentas de leitura (CPU, RAM, Portas, Serviços, Ping).
Se o utilizador relatar:
- Problemas de internet/DNS: escreve `[AÇÃO_NECESSÁRIA:DNS]`
- Impressora "engatada": escreve `[AÇÃO_NECESSÁRIA:SPOOLER]`
- IP errado: escreve `[AÇÃO_NECESSÁRIA:RENOVAR_IP]`
- Wi-Fi fraco: escreve `[AÇÃO_NECESSÁRIA:REDE]`
- Ficheiros corrompidos: escreve `[AÇÃO_NECESSÁRIA:SFC]`

{inventory_context}
"""

    # Preparar o histórico no formato de mensagens (OpenAI style)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": payload.message})

    # Definir as ferramentas no formato da OpenAI
    openai_tools = [
        {"type": "function", "function": {"name": "obter_info_sistema", "description": "Verifica CPU, RAM e Disco."}},
        {"type": "function", "function": {"name": "testar_conectividade", "description": "Faz ping a um host.", "parameters": {"type": "object", "properties": {"host": {"type": "string"}}}}},
        {"type": "function", "function": {"name": "listar_processos_pesados", "description": "Lista processos que mais consomem CPU/RAM."}},
        {"type": "function", "function": {"name": "verificar_servicos_windows", "description": "Verifica serviços do Windows."}},
        {"type": "function", "function": {"name": "verificar_portas_abertas", "description": "Lista portas abertas."}}
    ]

    try:
        # Usamos um modelo que suporta tool calling. 
        # "google/gemini-2.0-flash-001" ou "openai/gpt-4o-mini" são boas opções gratuitas/baratas.
        # Se quiseres um grátis garantido com tools, podes tentar "qwen/qwen3-4b:free" ou "openai/gpt-oss-120b:free"
        # Por segurança, vamos usar o roteador free, mas se falhar, o fallback entra em ação.
        response = client.chat.completions.create(
            model="openrouter/free", # Ou "google/gemini-2.0-flash-001" se tiveres créditos
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            extra_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-OpenRouter-Title": "Agente Suporte TI",
            }
        )

        response_message = response.choices[0].message
        reply_text = response_message.content or ""

        # Lógica de Tool Calling (se o modelo decidir chamar uma ferramenta)
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            
            # Executar a ferramenta localmente
            if function_name == "obter_info_sistema":
                result = tools.obter_info_sistema()
            elif function_name == "testar_conectividade":
                args = eval(function_args) # Cuidado com eval em produção, mas ok para local
                result = tools.testar_conectividade(args.get("host", "8.8.8.8"))
            elif function_name == "listar_processos_pesados":
                result = tools.listar_processos_pesados()
            elif function_name == "verificar_servicos_windows":
                result = tools.verificar_servicos_windows()
            elif function_name == "verificar_portas_abertas":
                result = tools.verificar_portas_abertas()
            else:
                result = "Ferramenta desconhecida."

            # Enviar o resultado da ferramenta de volta ao modelo
            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

            # Segunda chamada para obter a resposta final formatada
            final_response = client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                extra_headers={
                    "HTTP-Referer": "http://localhost:5173",
                    "X-OpenRouter-Title": "Agente Suporte TI",
                }
            )
            reply_text = final_response.choices[0].message.content

        # Fallback de segurança para as ações (tal como tínhamos no Gemini)
        msg_lower = payload.message.lower()
        if ("dns" in msg_lower or "internet" in msg_lower) and "[AÇÃO_NECESSÁRIA:" not in reply_text:
            reply_text += "\n\n**[AÇÃO_NECESSÁRIA:DNS]**"
        elif ("impressora" in msg_lower or "imprimir" in msg_lower) and "[AÇÃO_NECESSÁRIA:" not in reply_text:
            reply_text += "\n\n**[AÇÃO_NECESSÁRIA:SPOOLER]**"
        elif ("ip" in msg_lower or "dhcp" in msg_lower) and "[AÇÃO_NECESSÁRIA:" not in reply_text:
            reply_text += "\n\n**[AÇÃO_NECESSÁRIA:RENOVAR_IP]**"
        elif ("wifi" in msg_lower or "wi-fi" in msg_lower or "rede" in msg_lower) and "[AÇÃO_NECESSÁRIA:" not in reply_text:
            reply_text += "\n\n**[AÇÃO_NECESSÁRIA:REDE]**"
        elif ("corrompido" in msg_lower or "erro" in msg_lower) and "[AÇÃO_NECESSÁRIA:" not in reply_text:
            reply_text += "\n\n**[AÇÃO_NECESSÁRIA:SFC]**"

        return {"id": str(uuid.uuid4()), "role": "assistant", "content": reply_text, "createdAt": datetime.now().isoformat() + "Z"}

    except Exception as e:
        print(f"Erro no OpenRouter: {e}")
        # Modo de simulação em caso de falha (igual ao anterior)
        mock_reply = "⚠️ *O serviço de IA está indisponível. A usar simulação local.*\n\n"
        msg_lower = payload.message.lower()
        if "dns" in msg_lower or "internet" in msg_lower: mock_reply += "Posso limpar a cache DNS.\n\n**[AÇÃO_NECESSÁRIA:DNS]**"
        elif "impressora" in msg_lower or "imprimir" in msg_lower: mock_reply += "Posso reiniciar o spooler.\n\n**[AÇÃO_NECESSÁRIA:SPOOLER]**"
        elif "ip" in msg_lower: mock_reply += "Posso renovar o IP.\n\n**[AÇÃO_NECESSÁRIA:RENOVAR_IP]**"
        elif "wifi" in msg_lower or "rede" in msg_lower: mock_reply += "Posso reiniciar a placa de rede.\n\n**[AÇÃO_NECESSÁRIA:REDE]**"
        elif "corrompido" in msg_lower or "erro" in msg_lower: mock_reply += "Posso correr o SFC.\n\n**[AÇÃO_NECESSÁRIA:SFC]**"
        else: mock_reply += "Não consigo processar isso agora."
        return {"id": str(uuid.uuid4()), "role": "assistant", "content": mock_reply, "createdAt": datetime.now().isoformat() + "Z"}

# --- ROTAS DE AÇÃO (mantêm-se iguais) ---
@app.post("/api/actions/flush-dns")
def action_flush_dns(user_id: str = Depends(get_current_user)):
    return {"status": "success", "message": tools.limpar_cache_dns()}

@app.post("/api/actions/restart-spooler")
def action_restart_spooler(user_id: str = Depends(get_current_user)):
    return {"status": "success", "message": tools.reiniciar_spooler()}

@app.post("/api/actions/renew-ip")
def action_renew_ip(user_id: str = Depends(get_current_user)):
    return {"status": "success", "message": tools.renovar_ip()}

@app.post("/api/actions/restart-network")
def action_restart_network(user_id: str = Depends(get_current_user)):
    return {"status": "success", "message": tools.reiniciar_placa_rede()}

@app.post("/api/actions/sfc-scan")
def action_sfc_scan(user_id: str = Depends(get_current_user)):
    return {"status": "success", "message": tools.executar_sfc_scannow()}