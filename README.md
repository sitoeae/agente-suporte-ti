# 🤖 Agente de Suporte TI (IT Support Agent)

Uma plataforma de suporte técnico inteligente e automatizada, com um Agente de IA capaz de diagnosticar e resolver problemas de TI em tempo real, diretamente no PC do utilizador (Windows 10, 11 e Server).

## 🌟 Funcionalidades

- **Chat com IA:** Diagnóstico interativo em linguagem natural (pt-PT).
- **Agente Local (WebSockets):** Comunicação segura e em tempo real entre a nuvem e o PC do utilizador.
- **Tool Calling & Human-in-the-Loop:** A IA não executa comandos livremente. Ela sugere a correção e o utilizador autoriza com um clique.
- **Diagnósticos Reais:** Verifica estado do Spooler, filas de impressão, DNS, processos, CPU e RAM.
- **Gestão de Tickets:** Criação automática de tickets com o histórico do diagnóstico.
- **Inventário Contextualizado:** A IA conhece o hardware da empresa e cruza a informação no diagnóstico.
- **Segurança em Primeiro Lugar:** Autenticação JWT (Supabase), RLS (Row Level Security) e roles (User, Technician, Admin).

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura híbrida (Cloud + On-Premise):

```text
[ Frontend (Vercel) ] <----> [ Backend (Render) ] <----> [ Supabase (DB/Auth) ]
                                    ^
                                    | WebSockets
                                    v
[ Agente Local (PC do Utilizador) ] ---> Executa comandos no Windows
🛠️ Tecnologias Utilizadas
Frontend: React, TypeScript, Vite

Backend: Python, FastAPI

Base de Dados & Auth: PostgreSQL (Supabase)

Inteligência Artificial: OpenRouter (Modelos LLM) / Google Gemini

Comunicação Local: WebSockets

Deploy: Vercel (Frontend) e Render (Backend)

🚀 Como Executar o Projeto
1. Clonar o repositório
git clone https://github.com/O-TEU-USER/agente-suporte-ti.git
cd agente-suporte-ti

 Configurar o Frontend
bash
cd frontend
npm install
# Cria um ficheiro .env e adiciona as tuas chaves
npm run dev
3. Configurar o Backend
bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Cria um ficheiro .env e adiciona as tuas chaves
uvicorn main:app --reload
4. Executar o Agente Local (no PC do utilizador)
bash
cd agente_local
python agente_local.py

 Variáveis de Ambiente (.env)
Consulta os ficheiros .env.example nas pastas frontend e backend para saber que chaves são necessárias (Supabase, OpenRouter, etc). Nunca comites os teus ficheiros .env reais.

👨‍💻 Autor
Desenvolvido por [O Teu Nome].

LinkedIn

GitHub

text

### 🚀 Passo 3: Enviar tudo para o GitHub

No terminal, na raiz do projeto:

```powershell
git add .
git commit -m "docs: adicionar README profissional e limpar ficheiros residuais"
git push
🎉 FIM DO PROJETO!