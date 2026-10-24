export type DeviceType = "desktop" | "laptop" | "impressora" | "servidor" | "rede";

export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  serialNumber: string;
  location: string;
  os?: string;
  lastSeenAt?: string; // ISO 8601
}