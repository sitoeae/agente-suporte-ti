import type { ChatMessage as ChatMessageType } from "@/types/chat";
import { formatDate } from "@/utils/format";

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  return (
    <div className={`chat-message ${message.role}`}>
      {message.content}
      <span className="meta">
        {message.role === "user" ? "Tu" : "Agente"} · {formatDate(message.createdAt)}
      </span>
    </div>
  );
}