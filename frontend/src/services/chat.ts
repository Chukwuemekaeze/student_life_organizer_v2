import { http } from "@/services/http";

export type ChatThread = {
  id: number | string;
  title: string;
  created_at?: string;
  updated_at?: string;
};

export type ChatMessage = {
  id: number | string;
  thread_id: number | string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
};

export const ChatAPI = {
  listThreads: () => {
    console.log("ChatAPI.listThreads called");
    return http<ChatThread[]>(`/api/chat/threads`);
  },
  createThread: (title?: string) => {
    console.log("ChatAPI.createThread called with title:", title);
    return http<ChatThread>(`/api/chat/threads`, {
      method: "POST",
      body: JSON.stringify({ title }),
    });
  },
  listMessages: (threadId: number | string) =>
    http<ChatMessage[]>(`/api/chat/threads/${threadId}/messages`),
  sendMessage: (threadId: number | string, content: string) =>
    http<{ reply: string; tools?: any[]; thread_id: number }>(`/api/ai/chat`, {
      method: "POST",
      body: JSON.stringify({ message: content, thread_id: threadId }),
    }),
};
