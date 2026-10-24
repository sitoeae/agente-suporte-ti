import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/services/supabase";

export default function Sidebar() {
  const { user } = useAuth();
  const [role, setRole] = useState<string>("user");

  useEffect(() => {
    if (user) {
      supabase.from("profiles").select("role").eq("id", user.id).single()
        .then(({ data }) => {
          if (data) setRole(data.role);
        });
    }
  }, [user]);

  const links = [
    { to: "/dashboard", label: "Dashboard", roles: ["technician", "admin"] },
    { to: "/chat", label: "Chat de suporte", roles: ["user", "technician", "admin"] },
    { to: "/tickets", label: "Tickets", roles: ["user", "technician", "admin"] },
    { to: "/inventory", label: "Inventário", roles: ["technician", "admin"] },
    { to: "/knowledge", label: "Base de conhecimento", roles: ["technician", "admin"] },
    { to: "/settings", label: "Definições", roles: ["admin"] },
  ];

  const visibleLinks = links.filter(link => link.roles.includes(role));

  return (
    <aside className="app-sidebar">
      <div className="brand">Agente Suporte TI</div>
      <nav>
        {visibleLinks.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}