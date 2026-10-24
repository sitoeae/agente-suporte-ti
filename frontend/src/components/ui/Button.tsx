import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "primary";
  children: ReactNode;
}

export default function Button({
  variant = "default",
  className = "",
  children,
  ...rest
}: ButtonProps) {
  const classes = ["btn", variant === "primary" ? "primary" : "", className]
    .filter(Boolean)
    .join(" ");
  return (
    <button className={classes} {...rest}>
      {children}
    </button>
  );
}