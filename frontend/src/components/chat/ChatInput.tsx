import { useState, type FormEvent, type KeyboardEvent } from "react";
import Button from "@/components/ui/Button";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Descreve o teu problema técnico…",
}: Props) {
  const [text, setText] = useState("");

  function handleSubmit(e?: FormEvent) {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit} style={{ alignItems: "flex-end" }}>
      <textarea
        className="input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        style={{ resize: "none", minHeight: "42px", maxHeight: "120px", paddingTop: "0.6rem" }}
      />
      <Button type="submit" variant="primary" disabled={disabled || !text.trim()} style={{ height: "42px" }}>
        Enviar
      </Button>
    </form>
  );
}