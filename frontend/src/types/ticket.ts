export type TicketPriority = "baixa" | "media" | "alta" | "critica";
export type TicketStatus = "aberto" | "em_progresso" | "resolvido" | "fechado";
export type TicketCategory = "hardware" | "windows" | "redes" | "software" | "impressoras_hp" | "outro";

export interface Ticket {
  id: string;
  title: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  createdAt?: string; 
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
  assignee?: string;
}