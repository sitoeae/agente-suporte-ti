from fastapi import FastAPI, Depends, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid, os, asyncio, json
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from openai import OpenAI
from database import engine, get_db
import models
import jwt
from jwt import PyJWKClient

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agente Suporte TI API", version="3.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

openrouter_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
_jwks_client = PyJWKClient(f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json") if SUPABASE_URL else None

# --- GESTÃO DO WEBSOCKET ---
class AgentManager:
    def __init__(self):
        self.active_agent: Optional[WebSocket] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_agent = websocket

    def disconnect(self):
        self.active_agent = None

    async def send_command(self, acao: str) -> dict:
        if not self.active_agent:
            return {"status": "error", "message": "Agente Local offline."}
        req_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[req_id] = future
        try:
            await self.active_agent.send_text(json.dumps({"id": req_id, "acao": acao}))
            resultado = await asyncio.wait_for(future, timeout=15.0)
            return resultado
        except asyncio.TimeoutError:
            return {"status": "error", "message": "O PC demorou demasiado tempo."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.pending_requests.pop(req_id, None)

manager = AgentManager()

@app.websocket("/ws/agente")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            req_id = payload.get("id")
            if req_id in manager.pending_requests:
                manager.pending_requests[req_id].set_result(payload.get("resultado"))
    except WebSocketDisconnect:
        manager.disconnect()

# --- MODELOS PYDANTIC ---
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

# --- ROTAS CRUD ---
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

# --- CHAT INTELIGENTE ---
@app.post("/api/chat")
async def chat(payload: ChatPayload, db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    inventory_context = "INVENTÁRIO:\n" + "\n".join([f"- {d.asset_tag}: {d.manufacturer} {d.model} [{d.type}]" for d in devices])

    agent_status = "ONLINE" if manager.active_agent else "OFFLINE"
    
    # INSTRUÇÃO CRÍTICA PARA NÃO FAZER PERGUNTAS DESNECESSÁRIAS
    system_prompt = f"""
Tu és o "Agente Suporte TI", um técnico sénior especialista em Windows. Fala em pt-PT.
Estado do Agente Local: {agent_status}

DIRETRIZES DE DIAGNÓSTICO:
1. NUNCA faças ao utilizador perguntas cuja resposta possas obter através de uma ferramenta (ex: "qual é o estado do spooler?", "a impressora está instalada?").
2. Se o utilizador disser "a impressora não imprime", USA IMEDIATAMENTE a ferramenta `skill_diagnosticar_impressao`. Ela devolverá o estado do spooler, a fila e a LISTA de impressoras com os seus nomes e portas.
3. LÊ os dados que a ferramenta devolve (especialmente `impressoras_raw`). Se a impressora mencionada estiver "Offline" ou "Error" na lista, diz isso ao utilizador e sugere a correção.
4. Só deves fazer perguntas ao utilizador sobre coisas que o software não consegue ver (ex: "A impressora tem papel?", "O cabo USB está ligado?", "A luz verde está a piscar?").
5. Se os dados mostrarem que o Spooler está parado ou a fila presa, explica e adiciona a tag `[AÇÃO_NECESSÁRIA:SPOOLER]`.

{inventory_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.history: messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": payload.message})

    openai_tools = [
        {"type": "function", "function": {"name": "skill_diagnosticar_impressao", "description": "Vai buscar o estado real do spooler, fila e lista de impressoras no PC."}},
        {"type": "function", "function": {"name": "skill_diagnosticar_rede", "description": "Verifica a rede."}}
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
                
                if fn_name == "skill_diagnosticar_impressao":
                    res = await manager.send_command("diagnosticar_impressao")
                    result = json.dumps(res)
                elif fn_name == "skill_diagnosticar_rede":
                    res = await manager.send_command("diagnosticar_rede")
                    result = json.dumps(res)
                else:
                    result = "Desconhecido."
                
                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

            # A IA lê o JSON bruto das impressoras e formula a resposta final
            response = client.chat.completions.create(
                model="openrouter/free", messages=messages, tools=openai_tools, tool_choice="auto",
                extra_headers={"HTTP-Referer": "https://agente-suporte-ti.vercel.app", "X-OpenRouter-Title": "Agente"}
            )
            response_message = response.choices[0].message
            reply_text = response_message.content or ""

        return {"id": str(uuid.uuid4()), "role": "assistant", "content": reply_text, "createdAt": datetime.now().isoformat() + "Z"}
    except Exception as e:
        print(f"Erro IA: {e}")
        return {"id": str(uuid.uuid4()), "role": "system", "content": "Erro no cérebro da IA.", "createdAt": datetime.now().isoformat() + "Z"}

# --- ROTAS DE AÇÃO ---
@app.post("/api/actions/restart-spooler")
async def action_spooler(user_id: str = Depends(get_current_user)): 
    res = await manager.send_command("corrigir_spooler")
    return {"status": res.get("status", "error"), "message": res.get("message", "Erro")}

@app.post("/api/actions/flush-dns")
async def action_dns(user_id: str = Depends(get_current_user)): 
    res = await manager.send_command("limpar_dns")
    return {"status": res.get("status", "error"), "message": res.get("message", "Erro")}