import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement>;

export default function Input({ className = "", ...rest }: InputProps) {
  return <input className={`input ${className}`.trim()} {...rest} />;
}