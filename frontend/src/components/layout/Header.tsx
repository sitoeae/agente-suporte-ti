import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/services/supabase";
import Button from "@/components/ui/Button";
import { useNavigate } from "react-router-dom";

export default function Header() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState<string>("user");

  useEffect(() => {
    if (user) {
      // Vai buscar a role à tabela profiles
      supabase.from("profiles").select("role").eq("id", user.id).single()
        .then(({ data, error }) => {
          if (!error && data) {
            setRole(data.role);
          }
        });
    }
  }, [user]);

  async function handleSignOut() {
    try {
      await signOut();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Erro ao sair:", error);
    }
  }

  return (
    <header className="app-header">
      <strong>Suporte Técnico em TI</strong>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "1rem" }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", fontSize: 12 }}>
          <span style={{ color: "var(--text)" }}>{user?.email}</span>
          <span style={{ color: "var(--accent)", textTransform: "capitalize" }}>{role}</span>
        </div>
        <Button onClick={handleSignOut} style={{ padding: "0.25rem 0.5rem", fontSize: 12 }}>Sair</Button>
      </div>
    </header>
  );
}