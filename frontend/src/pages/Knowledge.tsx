import Card from "@/components/ui/Card";

interface Article {
  id: string;
  title: string;
  category: string;
  summary: string;
}

const articles: Article[] = [
  {
    id: "kb-001",
    title: "Windows não arranca após atualização",
    category: "Windows",
    summary:
      "Procedimento: arrancar em modo de segurança, verificar registo de atualizações, restaurar ponto anterior.",
  },
  {
    id: "kb-002",
    title: "Impressora HP offline em rede",
    category: "Impressoras HP",
    summary:
      "Verificar IP fixo, reiniciar spooler, reinstalar driver HP, testar porta 9100.",
  },
  {
    id: "kb-003",
    title: "Diagnóstico de RAM com MemTest",
    category: "Hardware",
    summary:
      "Correr MemTest86 a partir de USB, mínimo 2 passagens, verificar erros. Suspeita se >0.",
  },
  {
    id: "kb-004",
    title: "DNS não resolve nomes internos",
    category: "Redes",
    summary:
      "Confirmar servidor DNS configurado, testar nslookup, verificar DHCP e sufixo de domínio.",
  },
  {
    id: "kb-005",
    title: "Wi-Fi lento — passos de triagem",
    category: "Redes",
    summary:
      "Testar por cabo, verificar canal, analisar interferências, confirmar largura de banda no AP.",
  },
];

export default function Knowledge() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h1>Base de conhecimento</h1>
        <p style={{ color: "var(--text-muted)", margin: 0 }}>
          Procedimentos técnicos de exemplo. A pesquisa semântica (RAG) chega na fase 3.
        </p>
      </div>

      <div className="grid-cards">
        {articles.map((a) => (
          <Card key={a.id} title={a.title}>
            <div
              style={{
                fontSize: 11,
                color: "var(--accent)",
                textTransform: "uppercase",
                fontWeight: 600,
                marginBottom: 6,
              }}
            >
              {a.category}
            </div>
            <p style={{ color: "var(--text-muted)", margin: 0 }}>{a.summary}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}