import { supabase } from "./supabase";
import type { Ticket } from "@/types/ticket";
import type { Device } from "@/types/device";
import type { ChatMessage } from "@/types/chat";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = {
  getBaseUrl: () => API_URL,

  async listTickets(): Promise<Ticket[]> {
    const { data: { session } } = await supabase.auth.getSession();
    const res = await fetch(`${API_URL}/api/tickets`, {
      headers: { ...(session?.access_token ? { "Authorization": `Bearer ${session.access_token}` } : {}) }
    });
    if (!res.ok) throw new Error("Falha ao obter tickets");
    return res.json();
  },

  async createTicket(ticket: any): Promise<Ticket> {
    const { data: { session } } = await supabase.auth.getSession();
    const res = await fetch(`${API_URL}/api/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(session?.access_token ? { "Authorization": `Bearer ${session.access_token}` } : {}) },
      body: JSON.stringify(ticket),
    });
    if (!res.ok) throw new Error("Falha ao criar ticket");
    return res.json();
  },

  async listDevices(): Promise<any[]> {
    const { data: { session } } = await supabase.auth.getSession();
    const res = await fetch(`${API_URL}/api/devices`, {
      headers: { ...(session?.access_token ? { "Authorization": `Bearer ${session.access_token}` } : {}) }
    });
    if (!res.ok) throw new Error("Falha ao obter equipamentos");
    return res.json();
  },

  async createDevice(device: any): Promise<any> {
    const { data: { session } } = await supabase.auth.getSession();
    const res = await fetch(`${API_URL}/api/devices`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(session?.access_token ? { "Authorization": `Bearer ${session.access_token}` } : {}) },
      body: JSON.stringify(device),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Falha ao criar equipamento");
    }
    return res.json();
  },

  async sendChatMessage(history: ChatMessage[], text: string): Promise<ChatMessage> {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.map(h => ({ role: h.role, content: h.content })) }),
    });
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || "Erro de comunicação com o servidor.");
    }
    
    return res.json();
  },
};