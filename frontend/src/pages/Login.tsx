import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

export default function Login() {
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();
  
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      if (isRegister) {
        await signUp(email, password);
        alert("Conta criada com sucesso! Já podes fazer login.");
        setIsRegister(false); 
      } else {
        await signIn(email, password);
        navigate("/chat", { replace: true }); // Redireciona para o chat após login com sucesso
      }
    } catch (err: any) {
      console.error("ERRO NO LOGIN/REGISTO:", err); 
      setError(err.message || "Erro na autenticação. Verifica os dados.");
    } finally {
      setLoading(false); 
    }
  }

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", background: "var(--bg)" }}>
      <div style={{ width: "100%", maxWidth: "400px", padding: "1rem" }}>
        <Card title={isRegister ? "Criar Conta" : "Entrar no Agente TI"}>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && (
              <div style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid var(--danger)", padding: "0.75rem", borderRadius: "6px" }}>
                <p style={{ color: "var(--danger)", margin: 0, fontSize: 14 }}>{error}</p>
              </div>
            )}
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? "A processar..." : isRegister ? "Registar" : "Entrar"}
            </Button>
          </form>
          
          <div style={{ marginTop: "1rem", textAlign: "center", fontSize: 14 }}>
            <span style={{ color: "var(--text-muted)" }}>
              {isRegister ? "Já tens conta?" : "Ainda não tens conta?"}
            </span>{" "}
            <button 
              onClick={() => { setIsRegister(!isRegister); setError(""); }} 
              style={{ background: "none", border: "none", color: "var(--accent)", cursor: "pointer", padding: 0, font: "inherit" }}
            >
              {isRegister ? "Fazer Login" : "Registar"}
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
}