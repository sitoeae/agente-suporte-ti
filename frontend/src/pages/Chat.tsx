import { useState } from "react";
import ChatInput from "@/components/chat/ChatInput";
import Button from "@/components/ui/Button";
import { api } from "@/services/api";
import { generateId } from "@/utils/format";
import type { ChatMessage } from "@/types/chat";

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [creatingTicket, setCreatingTicket] = useState(false);

  async function handleSend(text: string) {
    const userMsg: ChatMessage = { id: generateId(), role: "user", content: text, createdAt: new Date().toISOString() };
    const history = [...messages, userMsg];
    setMessages(history);
    setLoading(true);

    const tempLoadingMsg: ChatMessage = { id: "loading-" + generateId(), role: "system", content: "A analisar...", createdAt: new Date().toISOString() };
    setMessages((prev) => [...prev, tempLoadingMsg]);

    try {
      const reply = await api.sendChatMessage(history, text);
      setMessages((prev) => prev.filter((m) => m.id !== tempLoadingMsg.id).concat(reply));
    } catch (err: any) {
      setMessages((prev) => prev.filter((m) => m.id !== tempLoadingMsg.id).concat({
        id: generateId(), role: "system", content: err.message || "Erro ao contactar o agente.", createdAt: new Date().toISOString()
      }));
    } finally {
      setLoading(false);
    }
  }

  // ... handleCreateTicket (igual, mantém-se) ...

  // NOVO: Executa a ação via AGENTE LOCAL (localhost)
  async function handleAction(actionType: string, successMsg: string) {
    setLoading(true);
    
    // Mapear os tipos de ação da UI para os comandos do Agente Local
    let agentAction = "";
    if (actionType === "SPOOLER") agentAction = "corrigir_spooler";
    else if (actionType === "DNS") agentAction = "limpar_dns";
    // ... adicionar as outras ações aqui
    
    try {
      const agentResponse = await api.callLocalAgent(agentAction);
      
      if (agentResponse.status === "success") {
        setMessages((prev) => [...prev, { id: generateId(), role: "system", content: `✅ ${agentResponse.message}`, createdAt: new Date().toISOString() }]);
      } else {
        setMessages((prev) => [...prev, { id: generateId(), role: "system", content: `❌ Erro: ${agentResponse.message}`, createdAt: new Date().toISOString() }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { id: generateId(), role: "system", content: "❌ Não foi possível contactar o Agente Local. Ele está a correr no teu PC?", createdAt: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  }

  const actionMap: Record<string, { label: string, endpoint: string }> = {
    "DNS": { label: "Limpar Cache DNS", endpoint: "DNS" },
    "SPOOLER": { label: "Reiniciar Serviço de Impressão", endpoint: "SPOOLER" },
    "RENOVAR_IP": { label: "Renovar Endereço IP", endpoint: "RENOVAR_IP" },
    "REDE": { label: "Reiniciar Placa de Rede", endpoint: "REDE" },
    "SFC": { label: "Verificar Ficheiros do Sistema", endpoint: "SFC" },
  };

  // ... (O resto do JSX mantém-se IGUAL ao anterior, mas o onClick do botão passa a chamar handleAction(actionMap[actionKey].endpoint, actionKey)) ...
  
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem", height: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div><h1>Chat de suporte</h1></div>
        {messages.some((m) => m.role === "assistant") && (
          <Button variant="primary" onClick={handleCreateTicket} disabled={creatingTicket}>Criar Ticket</Button>
        )}
      </div>

      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.75rem", minHeight: 0 }}>
        <div className="chat-messages">
          {messages.map((m) => {
            const actionsFound = Object.keys(actionMap).filter(key => m.content.includes(`[AÇÃO_NECESSÁRIA:${key}]`));
            let displayContent = m.content;
            actionsFound.forEach(key => {
              displayContent = displayContent.replace(`[AÇÃO_NECESSÁRIA:${key}]`, "").trim();
            });

            return (
              <div key={m.id} className={`chat-message ${m.role}`}>
                <div>{displayContent}</div>
                {actionsFound.length > 0 && (
                  <div style={{ marginTop: "1.5rem", padding: "1rem", background: "rgba(56, 189, 248, 0.1)", borderRadius: "8px", border: "1px solid var(--accent)" }}>
                    <p style={{ margin: "0 0 0.75rem", fontSize: "14px", fontWeight: "bold" }}>Ação recomendada (Requer Agente Local):</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                      {actionsFound.map(actionKey => (
                        <Button key={actionKey} variant="primary" onClick={() => handleAction(actionKey, actionKey)} disabled={loading}>
                          {actionMap[actionKey].label}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}