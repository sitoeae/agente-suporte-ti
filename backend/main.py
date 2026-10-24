from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid, os, asyncio, json
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from openai import OpenAI
from database import engine, get_db
import models
import jwt
from jwt import PyJWKClient

import tools
# Importar as novas skills
from skills import printing, network

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agente Suporte TI API", version="2.0.0 - Skills")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

openrouter_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

_jwks_client = PyJWKClient(f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json") if SUPABASE_URL else None

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

# ... (Rotas de Tickets e Devices mantêm-se iguais, omitidas aqui por brevidade, usa as anteriores) ...
@app.get("/api/tickets")
def get_tickets(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    user_profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()
    if user_profile.role in ["technician", "admin"]: return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()
    return db.query(models.Ticket).filter(models.Ticket.user_id == user_id).order_by(models.Ticket.created_at.desc()).all()

@app.post("/api/tickets")
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    novo = models.Ticket(user_id=user_id, title=ticket_in.title, description=ticket_in.description, category=ticket_in.category, priority=ticket_in.priority, status="aberto")
    db.add(novo); db.commit(); db.refresh(novo); return novo

@app.get("/api/devices")
def get_devices(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    return db.query(models.Device).order_by(models.Device.created_at.desc()).all()

@app.post("/api/devices")
def create_device(device_in: DeviceCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    user_profile = db.query(models.Profile).filter(models.Profile.id == user_id).first()
    if user_profile.role not in ["technician", "admin"]: raise HTTPException(status_code=403, detail="Não autorizado")
    novo = models.Device(**device_in.model_dump())
    db.add(novo); db.commit(); db.refresh(novo); return novo

# --- CHAT (O ORQUESTRADOR) ---
@app.post("/api/chat")
async def chat(payload: ChatPayload, db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    inventory_context = "INVENTÁRIO:\n" + "\n".join([f"- {d.asset_tag}: {d.manufacturer} {d.model}" for d in devices])

    system_prompt = f"""
Tu és o "Agente Suporte TI". Fala em português de Portugal (pt-PT).
O teu fluxo de trabalho é: Coletar -> Diagnosticar -> Sugerir Correção -> Validar.

Tens acesso a duas "Skills" de diagnóstico que executam verificações profundas no sistema:
1. `skill_diagnosticar_impressao`: Verifica spooler, fila, impressoras offline. Retorna um JSON.
2. `skill_diagnosticar_rede`: Verifica DNS, IP, DHCP. Retorna um JSON.

REGRAS:
- Se o utilizador disser que algo não imprime, USA OBRIGATORIAMENTE a `skill_diagnosticar_impressao`.
- Se o utilizador disser que a internet está falha, USA OBRIGATORIAMENTE a `skill_diagnosticar_rede`.
- Lê o JSON retornado pela skill. Se o `status` for "PROBLEMA_ENCONTRADO", explica ao utilizador e adiciona a tag da ação correspondente:
  - Para Spooler: `[AÇÃO_NECESSÁRIA:SPOOLER]`
  - Para DNS: `[AÇÃO_NECESSÁRIA:DNS]`
  - Para IP: `[AÇÃO_NECESSÁRIA:RENOVAR_IP]`
  - Para Rede Física: `[AÇÃO_NECESSÁRIA:REDE]`
- Se não houver ação, explica o que encontraste e diz que o problema pode ser físico ou externo.

{inventory_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.history: messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": payload.message})

    openai_tools = [
        {"type": "function", "function": {"name": "skill_diagnosticar_impressao", "description": "Executa um diagnóstico completo de impressão (spooler, fila, impressoras)."}},
        {"type": "function", "function": {"name": "skill_diagnosticar_rede", "description": "Executa um diagnóstico completo de rede (DNS, IP)."}},
        {"type": "function", "function": {"name": "obter_info_sistema", "description": "Verifica CPU e RAM."}},
        {"type": "function", "function": {"name": "testar_conectividade", "description": "Faz ping a um host.", "parameters": {"type": "object", "properties": {"host": {"type": "string"}}}}}
    ]

    try:
        response = client.chat.completions.create(
            model="openrouter/free", messages=messages, tools=openai_tools, tool_choice="auto",
            extra_headers={"HTTP-Referer": "https://agente-suporte-ti.vercel.app", "X-OpenRouter-Title": "Agente"}
        )

        response_message = response.choices[0].message
        reply_text = response_message.content or ""

        while response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments
                
                result = ""
                if fn_name == "skill_diagnosticar_impressao": result = printing.diagnosticar_impressao()
                elif fn_name == "skill_diagnosticar_rede": result = network.diagnosticar_rede()
                elif fn_name == "obter_info_sistema": result = tools.obter_info_sistema()
                elif fn_name == "testar_conectividade":
                    args = json.loads(fn_args)
                    result = tools.testar_conectividade(args.get("host", "8.8.8.8"))
                
                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

            response = client.chat.completions.create(
                model="openrouter/free", messages=messages, tools=openai_tools, tool_choice="auto",
                extra_headers={"HTTP-Referer": "https://agente-suporte-ti.vercel.app", "X-OpenRouter-Title": "Agente"}
            )
            response_message = response.choices[0].message
            reply_text = response_message.content or ""

        # Fallback
        msg_lower = payload.message.lower()
        if "[AÇÃO_NECESSÁRIA:" not in reply_text:
            if "impressora" in msg_lower or "imprimir" in msg_lower: reply_text += "\n\n**[AÇÃO_NECESSÁRIA:SPOOLER]**"
            elif "dns" in msg_lower: reply_text += "\n\n**[AÇÃO_NECESSÁRIA:DNS]**"

        return {"id": str(uuid.uuid4()), "role": "assistant", "content": reply_text, "createdAt": datetime.now().isoformat() + "Z"}
    except Exception as e:
        print(f"Erro IA: {e}")
        return {"id": str(uuid.uuid4()), "role": "system", "content": "Erro no cérebro da IA.", "createdAt": datetime.now().isoformat() + "Z"}

# --- ROTAS DE AÇÃO (Executam as Remediações das Skills) ---
@app.post("/api/actions/flush-dns")
def action_dns(user_id: str = Depends(get_current_user)): return {"status": "success", "message": network.corrigir_dns()}

@app.post("/api/actions/renew-ip")
def action_ip(user_id: str = Depends(get_current_user)): return {"status": "success", "message": network.corrigir_ip()}

@app.post("/api/actions/restart-network")
def action_net(user_id: str = Depends(get_current_user)): return {"status": "success", "message": network.reiniciar_rede()}

@app.post("/api/actions/restart-spooler")
def action_spooler(user_id: str = Depends(get_current_user)): return {"status": "success", "message": printing.corrigir_spooler()}