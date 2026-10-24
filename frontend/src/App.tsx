import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { useEffect, useState } from "react";
import { supabase } from "@/services/supabase";
import Layout from "@/components/layout/Layout";
import Dashboard from "@/pages/Dashboard";
import Chat from "@/pages/Chat";
import Tickets from "@/pages/Tickets";
import Inventory from "@/pages/Inventory";
import Knowledge from "@/pages/Knowledge";
import Settings from "@/pages/Settings";
import Login from "@/pages/Login";

// Componente para proteger rotas por Role
function RoleRoute({ allowedRoles, children }: { allowedRoles: string[], children: React.ReactNode }) {
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      supabase.from("profiles").select("role").eq("id", user.id).single()
        .then(({ data }) => {
          setRole(data?.role || "user");
          setLoading(false);
        });
    }
  }, [user]);

  if (loading) return <div style={{ padding: "2rem", color: "var(--text)" }}>A validar permissões...</div>;
  if (!role || !allowedRoles.includes(role)) return <Navigate to="/chat" replace />;
  
  return <>{children}</>;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", color: "var(--text)" }}>A carregar sistema...</div>;
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/chat" replace />} />
      <Route element={<Layout />}>
        {/* Redirecionamento inicial */}
        <Route index element={<Navigate to="/chat" replace />} />
        
        <Route path="chat" element={<Chat />} />
        <Route path="tickets" element={<Tickets />} />
        
        {/* Rotas Protegidas */}
        <Route path="dashboard" element={
          <RoleRoute allowedRoles={["technician", "admin"]}>
            <Dashboard />
          </RoleRoute>
        } />
        <Route path="inventory" element={
          <RoleRoute allowedRoles={["technician", "admin"]}>
            <Inventory />
          </RoleRoute>
        } />
        <Route path="knowledge" element={
          <RoleRoute allowedRoles={["technician", "admin"]}>
            <Knowledge />
          </RoleRoute>
        } />
        <Route path="settings" element={
          <RoleRoute allowedRoles={["admin"]}>
            <Settings />
          </RoleRoute>
        } />
        
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}