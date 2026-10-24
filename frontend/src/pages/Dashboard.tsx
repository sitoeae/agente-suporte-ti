import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { api } from "@/services/api";
import { formatDate } from "@/utils/format";
import type { Ticket } from "@/types/ticket";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [deviceCount, setDeviceCount] = useState<number>(0);

  useEffect(() => {
    // Vai buscar os tickets e os equipamentos em paralelo
    Promise.all([
      api.listTickets(),
      api.listDevices()
    ]).then(([ticketsData, devicesData]) => {
      setTickets(ticketsData);
      setDeviceCount(devicesData.length);
    }).catch(err => {
      console.error("Erro ao carregar dados do dashboard:", err);
    });
  }, []);

  const abertos = tickets.filter((t) => t.status === "aberto").length;
  const emProgresso = tickets.filter((t) => t.status === "em_progresso").length;
  const criticos = tickets.filter((t) => t.priority === "critica").length;
  
  const recentes = [...tickets]
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(0, 3);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div>
        <h1>Dashboard</h1>
        <p style={{ color: "var(--text-muted)", margin: 0 }}>
          Visão geral do suporte técnico.
        </p>
      </div>

      <div className="grid-cards">
        <Card title="Tickets abertos">
          <div style={{ fontSize: 28, fontWeight: 700 }}>{abertos}</div>
        </Card>
        <Card title="Em progresso">
          <div style={{ fontSize: 28, fontWeight: 700 }}>{emProgresso}</div>
        </Card>
        <Card title="Prioridade crítica">
          <div style={{ fontSize: 28, fontWeight: 700, color: "var(--danger)" }}>
            {criticos}
          </div>
        </Card>
        <Card title="Equipamentos">
          <div style={{ fontSize: 28, fontWeight: 700 }}>{deviceCount}</div>
        </Card>
      </div>

      <Card title="Incidentes recentes">
        {recentes.length === 0 ? (
          <p style={{ color: "var(--text-muted)", margin: 0 }}>Sem dados.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {recentes.map((t) => (
              <li
                key={t.id}
                style={{
                  padding: "0.6rem 0",
                  borderBottom: "1px solid var(--border)",
                  display: "flex",
                  gap: "0.75rem",
                  alignItems: "center",
                }}
              >
                <Badge variant={t.priority}>{t.priority}</Badge>
                <span style={{ flex: 1 }}>{t.title}</span>
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {formatDate(t.created_at || t.createdAt)}
                </span>
              </li>
            ))}
          </ul>
        )}
        <div style={{ marginTop: "0.75rem" }}>
          <Link to="/tickets" className="btn" style={{ display: "inline-block" }}>
            Ver todos os tickets
          </Link>
        </div>
      </Card>
    </div>
  );
}