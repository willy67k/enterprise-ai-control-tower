import React from "react";
import ReactMarkdown from "react-markdown";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
  provider?: string;
}

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-2xl rounded-2xl px-4 py-3 text-sm ${isUser ? "bg-indigo-600 text-white" : "bg-white text-gray-800 shadow-sm ring-1 ring-gray-200"}`}>
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm prose-p:my-1 prose-pre:bg-gray-100 prose-pre:text-xs max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
        {message.model && (
          <p className="mt-1.5 text-xs opacity-60">
            {message.provider} · {message.model}
          </p>
        )}
      </div>
    </div>
  );
};
