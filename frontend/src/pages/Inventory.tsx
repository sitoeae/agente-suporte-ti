import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { api } from "@/services/api";

export default function Inventory() {
  const [devices, setDevices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    asset_tag: "", type: "Laptop", manufacturer: "", model: "", serial_number: "",
    assigned_to: "", location: "", status: "Em uso", os: "",
    network_name: "", ip_address: "", mac_address: "", ip_type: "Dinâmico", server_role: ""
  });
  const [error, setError] = useState("");

  async function loadDevices() {
    try {
      const data = await api.listDevices();
      setDevices(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadDevices(); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.createDevice(formData);
      setShowForm(false);
      setFormData({ asset_tag: "", type: "Laptop", manufacturer: "", model: "", serial_number: "", assigned_to: "", location: "", status: "Em uso", os: "", network_name: "", ip_address: "", mac_address: "", ip_type: "Dinâmico", server_role: "" });
      loadDevices();
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Inventário de Equipamentos</h1>
          <p style={{ color: "var(--text-muted)", margin: 0 }}>Gestão de hardware e rede.</p>
        </div>
        <Button variant="primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancelar" : "+ Novo Equipamento"}
        </Button>
      </div>

      {showForm && (
        <Card title="Adicionar Equipamento">
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {error && <p style={{ color: "var(--danger)", margin: 0 }}>{error}</p>}
            
            {/* Bloco 1: Identificação */}
            <div>
              <h4 style={{ color: "var(--accent)", marginBottom: "0.5rem" }}>1. Identificação</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
                <Input placeholder="Código de Ativo *" value={formData.asset_tag} onChange={e => setFormData({...formData, asset_tag: e.target.value})} required />
                <select className="input" value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})}>
                  <option value="Laptop">Laptop</option>
                  <option value="Desktop">Desktop</option>
                  <option value="Impressora">Impressora</option>
                  <option value="Servidor">Servidor</option>
                  <option value="Rede">Equip. Rede (Switch/Router)</option>
                </select>
                <Input placeholder="Número de Série" value={formData.serial_number} onChange={e => setFormData({...formData, serial_number: e.target.value})} />
                <Input placeholder="Fabricante (ex: Dell)" value={formData.manufacturer} onChange={e => setFormData({...formData, manufacturer: e.target.value})} />
                <Input placeholder="Modelo" value={formData.model} onChange={e => setFormData({...formData, model: e.target.value})} />
                <Input placeholder="Sistema Operativo" value={formData.os} onChange={e => setFormData({...formData, os: e.target.value})} />
              </div>
            </div>

            {/* Bloco 2: Atribuição */}
            <div>
              <h4 style={{ color: "var(--accent)", marginBottom: "0.5rem" }}>2. Localização e Atribuição</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
                <Input placeholder="Responsável (Nome)" value={formData.assigned_to} onChange={e => setFormData({...formData, assigned_to: e.target.value})} />
                <Input placeholder="Localização (ex: Piso 2)" value={formData.location} onChange={e => setFormData({...formData, location: e.target.value})} />
                <select className="input" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                  <option value="Em uso">Em uso</option>
                  <option value="Stock">Em stock</option>
                  <option value="Reparação">Em reparação</option>
                  <option value="Abatido">Abatido</option>
                </select>
              </div>
            </div>

            {/* Bloco 3: Rede e Segurança */}
            <div>
              <h4 style={{ color: "var(--accent)", marginBottom: "0.5rem" }}>3. Rede e Segurança</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
                <Input placeholder="Nome na Rede (ex: DESKTOP-FIN)" value={formData.network_name} onChange={e => setFormData({...formData, network_name: e.target.value})} />
                <Input placeholder="Endereço IP" value={formData.ip_address} onChange={e => setFormData({...formData, ip_address: e.target.value})} />
                <select className="input" value={formData.ip_type} onChange={e => setFormData({...formData, ip_type: e.target.value})}>
                  <option value="Dinâmico">IP Dinâmico (DHCP)</option>
                  <option value="Estático">IP Estático</option>
                </select>
                <Input placeholder="Endereço MAC" value={formData.mac_address} onChange={e => setFormData({...formData, mac_address: e.target.value})} />
                
                {formData.type === "Servidor" && (
                  <select className="input" value={formData.server_role} onChange={e => setFormData({...formData, server_role: e.target.value})}>
                    <option value="">Função do Servidor...</option>
                    <option value="DNS">Servidor DNS</option>
                    <option value="DHCP">Servidor DHCP</option>
                    <option value="Ficheiros">Servidor de Ficheiros</option>
                    <option value="Web">Servidor Web</option>
                    <option value="Base de Dados">Base de Dados</option>
                    <option value="Domínio (AD)">Controlador de Domínio (AD)</option>
                    <option value="Outro">Outro</option>
                  </select>
                )}
              </div>
            </div>
            
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button type="submit" variant="primary">Guardar Equipamento</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {loading ? (
          <p>A carregar inventário...</p>
        ) : devices.length === 0 ? (
          <p style={{ color: "var(--text-muted)", textAlign: "center" }}>Nenhum equipamento registado.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "var(--text-muted)", fontSize: 12 }}>
                <th style={{ padding: "0.5rem" }}>Ativo / Tipo</th>
                <th style={{ padding: "0.5rem" }}>Rede / IP</th>
                <th style={{ padding: "0.5rem" }}>Responsável</th>
                <th style={{ padding: "0.5rem" }}>Estado</th>
              </tr>
            </thead>
            <tbody>
              {devices.map(d => (
                <tr key={d.id} style={{ borderTop: "1px solid var(--border)" }}>
                  <td style={{ padding: "0.5rem" }}>
                    <div style={{ fontWeight: "bold" }}>{d.asset_tag}</div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{d.type} {d.server_role ? `(${d.server_role})` : ''}</div>
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <div>{d.ip_address || "—"}</div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{d.network_name || ""}</div>
                  </td>
                  <td style={{ padding: "0.5rem" }}>{d.assigned_to || "—"}</td>
                  <td style={{ padding: "0.5rem", color: d.status === 'Em uso' ? 'var(--success)' : 'var(--warning)' }}>{d.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}