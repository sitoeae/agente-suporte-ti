# Agente de Suporte Técnico em TI

Plataforma de suporte técnico inteligente com agente de IA, gestão de
incidentes, base de conhecimento e agente local de diagnóstico para Windows.

## Âmbito

- Suporte técnico de 1.º e 2.º nível
- Hardware, Windows, redes, software e impressoras HP
- Help desk: tickets, prioridades, histórico
- Base de conhecimento com pesquisa (RAG na fase 3)
- Agente Windows com diagnósticos autorizados (fase 4)

## Arquitetura

Híbrida:
- **Frontend** — React + TypeScript + Vite
- **Backend** — Python + FastAPI (fase 2)
- **Base de dados** — PostgreSQL / Supabase
- **IA** — API online (modelo definido na fase 3)
- **Agente Windows** — Python, emparelhamento seguro (fase 4)

## Estrutura do repositório
