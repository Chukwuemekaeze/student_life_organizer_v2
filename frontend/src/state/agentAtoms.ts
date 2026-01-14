import { atom } from "jotai";
import type { AgentToolCall } from "../services/agent";

export type ChatMsg = { 
  id: string; 
  role: "user" | "assistant"; 
  text: string; 
  tool_calls?: AgentToolCall[] 
};

export const agentMessagesAtom = atom<ChatMsg[]>([]);
export const agentLoadingAtom = atom<boolean>(false);
export const agentConfirmWritesAtom = atom<boolean>(true);
