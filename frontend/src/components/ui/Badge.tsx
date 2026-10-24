import type { ReactNode } from "react";

type Variant = "baixa" | "media" | "alta" | "critica" | "neutral";

interface BadgeProps {
  variant?: Variant;
  children: ReactNode;
}

export default function Badge({ variant = "neutral", children }: BadgeProps) {
  return <span className={`badge ${variant}`}>{children}</span>;
}