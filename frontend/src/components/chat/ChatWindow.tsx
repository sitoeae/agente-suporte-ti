import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import ChatMessage from "./ChatMessage";

interface Props {
  messages: ChatMessageType[];
}

export default function ChatWindow({ messages }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-messages" ref={ref}>
      {messages.length === 0 && (
        <div className="chat-message system">
          Descreve o problema (hardware, Windows, redes, software ou impressoras HP)
          para começar o diagnóstico.
        </div>
      )}
      {messages.map((m) => (
        <ChatMessage key={m.id} message={m} />
      ))}
    </div>
  );
}