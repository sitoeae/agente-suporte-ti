import Card from "@/components/ui/Card";
import { api } from "@/services/api";

export default function Settings() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h1>Definições</h1>
        <p style={{ color: "var(--text-muted)", margin: 0 }}>
          Estado da configuração atual do MVP.
        </p>
      </div>

      <Card title="Backend">
        <p style={{ margin: 0 }}>
          URL da API:{" "}
          <code style={{ background: "var(--bg)", padding: "0.15rem 0.4rem", borderRadius: 4 }}>
            {api.getBaseUrl()}
          </code>
        </p>
        <p style={{ color: "var(--text-muted)", margin: "0.5rem 0 0" }}>
          Ainda não ligado — fase 2 do roadmap.
        </p>
      </Card>

      <Card title="Estado do projeto">
        <ul style={{ margin: 0, paddingLeft: "1.2rem", lineHeight: 1.7 }}>
          <li>✅ Frontend (mocks)</li>
          <li>⏳ Backend FastAPI</li>
          <li>⏳ Integração IA online</li>
          <li>⏳ Base de dados + autenticação</li>
          <li>⏳ Agente Windows</li>
          <li>⏳ Deploy e produção</li>
        </ul>
      </Card>

      <Card title="Segurança">
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          Este MVP não deve ser exposto à Internet. Autenticação, permissões e auditoria
          serão implementadas antes da fase de produção.
        </p>
      </Card>
    </div>
  );
}