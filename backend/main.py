# Adiciona isto no ChatPayload
class ChatPayload(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    local_agent_online: bool = False # <-- NOVO

# Dentro da função @app.post("/api/chat"):
@app.post("/api/chat")
async def chat(payload: ChatPayload, db: Session = Depends(get_db)):
    # ... (obter o inventário igual) ...

    agent_status = "ONLINE" if payload.local_agent_online else "OFFLINE"
    
    system_prompt = f"""
Tu és o "Agente Suporte TI". Fala em português de Portugal (pt-PT).
CONTEXTO: Assumes que o utilizador está num Windows 10, 11 ou Server.
ESTADO DO AGENTE LOCAL NO PC DO UTILIZADOR: {agent_status}

REGRAS:
- Se o utilizador se queixar de algo (ex: "não imprime", "internet falha") e o Agente Local estiver **ONLINE**:
  -> Usa a ferramenta `skill_diagnosticar_impressao` ou `skill_diagnosticar_rede` para mandar o PC fazer o teste. (O Frontend encarrega-se de apanhar o botão de ação).
- Se o utilizador se queixar e o Agente Local estiver **OFFLINE**:
  -> Diz ao utilizador: "Para eu conseguir verificar o teu PC e corrigir o problema automaticamente, precisas de descarregar e correr o Agente Local." E dá-lhe as instruções simples.
- NUNCA faças tu o diagnóstico falso. Deixa as ferramentas fazerem o trabalho.

{inventory_context}
"""

    # ... (o resto do código da chamada à IA fica igual) ...

    messages = [{"role": "system", "content": system_prompt}]
    for msg in payload.history: messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": payload.message})

    openai_tools = [
        {"type": "function", "function": {"name": "skill_diagnosticar_impressao", "description": "Diagnóstico de impressão."}},
        {"type": "function", "function": {"name": "skill_diagnosticar_rede", "description": "Diagnóstico de rede."}},
        {"type": "function", "function": {"name": "obter_info_sistema", "description": "Verifica CPU e RAM."}}
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
                # O backend já não corre a skill de verdade, apenas simula a resposta para o frontend saber o que fazer
                if fn_name == "skill_diagnosticar_impressao": result = "Diagnóstico solicitado. O Frontend irá tratar."
                elif fn_name == "skill_diagnosticar_rede": result = "Diagnóstico solicitado. O Frontend irá tratar."
                elif fn_name == "obter_info_sistema": result = tools.obter_info_sistema()
                else: result = "Desconhecido."
                
                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

            response = client.chat.completions.create(
                model="openrouter/free", messages=messages, tools=openai_tools, tool_choice="auto",
                extra_headers={"HTTP-Referer": "https://agente-suporte-ti.vercel.app", "X-OpenRouter-Title": "Agente"}
            )
            response_message = response.choices[0].message
            reply_text = response_message.content or ""

        msg_lower = payload.message.lower()
        if "[AÇÃO_NECESSÁRIA:" not in reply_text:
            if "impressora" in msg_lower or "imprimir" in msg_lower: reply_text += "\n\n**[AÇÃO_NECESSÁRIA:SPOOLER]**"
            elif "dns" in msg_lower or "internet" in msg_lower: reply_text += "\n\n**[AÇÃO_NECESSÁRIA:DNS]**"

        return {"id": str(uuid.uuid4()), "role": "assistant", "content": reply_text, "createdAt": datetime.now().isoformat() + "Z"}
    except Exception as e:
        print(f"Erro IA: {e}")
        return {"id": str(uuid.uuid4()), "role": "system", "content": "Serviço de IA offline.", "createdAt": datetime.now().isoformat() + "Z"}