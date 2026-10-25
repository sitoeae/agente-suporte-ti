import { useState } from "react";
import ChatInput from "@/components/chat/ChatInput";
import Button from "@/components/ui/Button";
import { api } from "@/services/api";
import { generateId } from "@/utils/format";
import type { ChatMessage } from "@/types/chat";
import { supabase } from "@/services/supabase";

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

  async function handleCreateTicket() {
    const firstUserMsg = messages.find((m) => m.role === "user");
    const lastAiMsg = [...messages].reverse().find((m) => m.role === "assistant");
    if (!firstUserMsg || !lastAiMsg) return;
    
    setCreatingTicket(true);
    try {
      const fullText = (firstUserMsg.content + " " + lastAiMsg.content).toLowerCase();
      let category = "outro";
      if (fullText.includes("windows") || fullText.includes("pc")) category = "windows";
      else if (fullText.includes("rede") || fullText.includes("internet")) category = "redes";
      else if (fullText.includes("impressora") || fullText.includes("hp")) category = "impressoras_hp";
      
      await api.createTicket({ title: firstUserMsg.content.substring(0, 80), description: lastAiMsg.content, category, priority: "media" });
      alert("Ticket criado!");
    } catch (err) { 
      alert("Erro ao criar ticket."); 
    } finally { 
      setCreatingTicket(false); 
    }
  }

  async function handleAction(actionType: string) {
    setLoading(true);
    
    let endpoint = "";
    if (actionType === "SPOOLER") endpoint = "/api/actions/restart-spooler";
    else if (actionType === "DNS") endpoint = "/api/actions/flush-dns";
    
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const res = await fetch(`${import.meta.env.VITE_API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${session?.access_token}` }
      });
      
      if (!res.ok) throw new Error("Falha na API");
      
      const data = await res.json();
      setMessages((prev) => [...prev, { id: generateId(), role: "system", content: `✅ ${data.message}`, createdAt: new Date().toISOString() }]);
    } catch (err) {
      setMessages((prev) => [...prev, { id: generateId(), role: "system", content: `❌ Erro ao executar a ação no PC.`, createdAt: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  }

  const actionMap: Record<string, { label: string }> = {
    "DNS": { label: "Limpar Cache DNS" },
    "SPOOLER": { label: "Reiniciar Serviço de Impressão" },
    "RENOVAR_IP": { label: "Renovar Endereço IP" },
    "REDE": { label: "Reiniciar Placa de Rede" },
    "SFC": { label: "Verificar Ficheiros do Sistema" },
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem", height: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div><h1>Chat de suporte</h1></div>
        {messages.some((m) => m.role === "assistant") && (
          <Button variant="primary" onClick={handleCreateTicket} disabled={creatingTicket}>
            {creatingTicket ? "A criar..." : "Criar Ticket"}
          </Button>
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
                    <p style={{ margin: "0 0 0.75rem", fontSize: "14px", fontWeight: "bold" }}>Ação recomendada pelo agente:</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                      {actionsFound.map(actionKey => (
                        <Button key={actionKey} variant="primary" onClick={() => handleAction(actionKey)} disabled={loading}>
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