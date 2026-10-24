import { useEffect, useMemo, useState } from "react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/services/api";
import { formatDate, shortId } from "@/utils/format";
import type { Ticket, TicketStatus, TicketPriority } from "@/types/ticket";

const statuses: Array<{ value: TicketStatus | "todos"; label: string }> = [
  { value: "todos", label: "Todos" },
  { value: "aberto", label: "Aberto" },
  { value: "em_progresso", label: "Em progresso" },
  { value: "resolvido", label: "Resolvido" },
  { value: "fechado", label: "Fechado" },
];

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TicketStatus | "todos">("todos");

  // Estados do formulário
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TicketPriority>("media");
  const [loading, setLoading] = useState(false);

  async function loadTickets() {
    try {
      const data = await api.listTickets();
      setTickets(data);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    try {
      await api.createTicket({
        title,
        description,
        category: "outro",
        priority,
      });
      // Limpar o formulário e recarregar a lista
      setTitle("");
      setDescription("");
      setPriority("media");
      setShowForm(false);
      await loadTickets();
    } catch (err) {
      alert("Erro ao criar ticket. Verifica a consola.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      const matchesQuery =
        !query ||
        t.title.toLowerCase().includes(query.toLowerCase()) ||
        t.description?.toLowerCase().includes(query.toLowerCase());
      const matchesStatus = statusFilter === "todos" || t.status === statusFilter;
      return matchesQuery && matchesStatus;
    });
  }, [tickets, query, statusFilter]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Tickets</h1>
          <p style={{ color: "var(--text-muted)", margin: 0 }}>
            Gestão de incidentes de suporte.
          </p>
        </div>
        <Button variant="primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancelar" : "+ Novo Ticket"}
        </Button>
      </div>

      {showForm && (
        <Card title="Criar novo ticket">
          <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <Input
              placeholder="Título (ex: PC não liga)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <textarea
              className="input"
              placeholder="Descrição detalhada do problema..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
            <select
              className="input"
              value={priority}
              onChange={(e) => setPriority(e.target.value as TicketPriority)}
            >
              <option value="baixa">Baixa</option>
              <option value="media">Média</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? "A guardar..." : "Guardar Ticket"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <Input
            placeholder="Pesquisar por título ou descrição…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: 1, minWidth: 220 }}
          />
          <select
            className="input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as TicketStatus | "todos")}
            style={{ maxWidth: 200 }}
          >
            {statuses.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>

        {filtered.length === 0 ? (
          <p style={{ color: "var(--text-muted)", margin: 0, textAlign: "center", padding: "2rem 0" }}>
            Nenhum ticket encontrado. Clica em "+ Novo Ticket" para criar o primeiro.
          </p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "var(--text-muted)", fontSize: 12 }}>
                <th style={{ padding: "0.5rem" }}>ID</th>
                <th style={{ padding: "0.5rem" }}>Título</th>
                <th style={{ padding: "0.5rem" }}>Prioridade</th>
                <th style={{ padding: "0.5rem" }}>Estado</th>
                <th style={{ padding: "0.5rem" }}>Criado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id} style={{ borderTop: "1px solid var(--border)" }}>
                  <td style={{ padding: "0.5rem", fontFamily: "monospace", color: "var(--text-muted)" }}>
                    {shortId(t.id)}
                  </td>
                  <td style={{ padding: "0.5rem" }}>{t.title}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <Badge variant={t.priority}>{t.priority}</Badge>
                  </td>
                  <td style={{ padding: "0.5rem" }}>{t.status.replace("_", " ")}</td>
                  <td style={{ padding: "0.5rem", color: "var(--text-muted)", fontSize: 12 }}>
                    {formatDate(t.createdAt || new Date().toISOString())}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}