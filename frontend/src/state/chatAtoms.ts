import { atom } from "jotai";
import type { ChatThread, ChatMessage } from "@/services/chat";

export const threadsAtom = atom<ChatThread[]>([]);
export const messagesAtom = atom<Record<string, ChatMessage[]>>({});
export const currentThreadIdAtom = atom<string | number | null>(null);
export const loadingThreadsAtom = atom<boolean>(false);
export const sendingAtom = atom<boolean>(false);



