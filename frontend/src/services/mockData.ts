import type { Ticket } from "@/types/ticket";
import type { Device } from "@/types/device";

export const mockTickets: Ticket[] = [
  {
    id: "t-0001",
    title: "PC não arranca após atualização do Windows",
    description:
      "Após a última atualização, o computador fica preso no ecrã de arranque.",
    category: "windows",
    priority: "alta",
    status: "aberto",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    assignee: "Técnico A",
  },
  {
    id: "t-0002",
    title: "Impressora HP não imprime em rede",
    description:
      "A impressora HP LaserJet aparece offline para todos os utilizadores do piso 2.",
    category: "impressoras_hp",
    priority: "media",
    status: "em_progresso",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    assignee: "Técnico B",
  },
  {
    id: "t-0003",
    title: "Wi-Fi lento no escritório central",
    description:
      "Vários utilizadores reportam internet lenta na rede Wi-Fi corporativa.",
    category: "redes",
    priority: "critica",
    status: "aberto",
    createdAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  },
];

export const mockDevices: Device[] = [
  {
    id: "d-0001",
    name: "PC-RECEPCAO-01",
    type: "desktop",
    serialNumber: "SN-DSK-0001",
    location: "Receção",
    os: "Windows 11 Pro",
    lastSeenAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: "d-0002",
    name: "LAPTOP-FINANCEIRO-02",
    type: "laptop",
    serialNumber: "SN-LTP-0002",
    location: "Financeiro",
    os: "Windows 10 Pro",
    lastSeenAt: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "d-0003",
    name: "HP-LASERJET-PISO2",
    type: "impressora",
    serialNumber: "SN-HP-0003",
    location: "Piso 2",
    lastSeenAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
];