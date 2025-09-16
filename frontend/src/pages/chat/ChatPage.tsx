import { useEffect, useState } from "react";
import { useAtom } from "jotai";
import {
  threadsAtom,
  messagesAtom,
  currentThreadIdAtom,
  loadingThreadsAtom,
  sendingAtom,
} from "@/state/chatAtoms";
import { ChatAPI } from "@/services/chat";
import ThreadList from "@/components/chat/ThreadList";
import MessagePane from "@/components/chat/MessagePane";
import MessageInput from "@/components/chat/MessageInput";

export default function ChatPage() {
  console.log("ChatPage component mounted!");
  const [threads, setThreads] = useAtom(threadsAtom);
  const [messages, setMessages] = useAtom(messagesAtom);
  const [currentId, setCurrentId] = useAtom(currentThreadIdAtom);
  const [loading, setLoading] = useAtom(loadingThreadsAtom);
  const [sending, setSending] = useAtom(sendingAtom);
  const [sidebarVisible, setSidebarVisible] = useState(true);

  // Load thread list on mount
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await ChatAPI.listThreads();
        setThreads(data);
        if (!currentId && data[0]) setCurrentId(data[0].id);
      } catch (e) {
        console.error("Failed to load threads", e);
        // Keep UI usable without toasts to avoid spam
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load messages when current thread changes
  useEffect(() => {
    if (!currentId) return;
    (async () => {
      try {
        const msgs = await ChatAPI.listMessages(currentId);
        setMessages((prev) => ({ ...prev, [String(currentId)]: msgs }));
      } catch (e) {
        console.error("Failed to load messages", e);
      }
    })();
  }, [currentId, setMessages]);

  async function handleCreateThread() {
    try {
      console.log("Creating new thread...");
      const t = await ChatAPI.createThread();
      console.log("Thread created:", t);
      setThreads((prev) => [t, ...prev]);
      setCurrentId(t.id);
      setMessages((prev) => ({ ...prev, [String(t.id)]: [] }));
      console.log("Thread set as current:", t.id);
    } catch (e) {
      console.error("Failed to create thread", e);
    }
  }

  async function handleSend(text: string) {
    console.log("handleSend called with:", text, "currentId:", currentId);
    if (!currentId) {
      console.log("No current thread selected, cannot send message");
      return;
    }
    try {
      setSending(true);
      console.log("Sending message to thread:", currentId);
      // Optimistic insert (user)
      setMessages((prev) => {
        const key = String(currentId);
        const next = [...(prev[key] || [])];
        next.push({ id: `temp-${Date.now()}`, thread_id: currentId, role: "user", content: text });
        return { ...prev, [key]: next };
      });

      // Send to backend (AI endpoint)
      const aiResponse = await ChatAPI.sendMessage(currentId, text);
      console.log("AI response received:", aiResponse);

      // Refresh thread messages (including both user message and AI reply)
      const fresh = await ChatAPI.listMessages(currentId);
      console.log("Refreshed messages:", fresh);
      setMessages((p) => ({ ...p, [String(currentId)]: fresh }));
    } catch (e) {
      console.error("Failed to send message", e);
    } finally {
      setSending(false);
    }
  }

  const currentMsgs = messages[String(currentId ?? "")] || [];

  return (
    <div className="flex h-[calc(100vh-8rem)] bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Mobile backdrop */}
      <div className="lg:hidden fixed inset-0 bg-black/20 z-40 hidden" id="sidebar-backdrop" onClick={() => {
        const sidebar = document.getElementById('chat-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');
        sidebar?.classList.add('-translate-x-full');
        backdrop?.classList.add('hidden');
      }} />
      
      {/* Chat Sidebar */}
      <div className={`bg-gray-50 border-r border-gray-200 flex flex-col transition-all duration-200 ease-in-out z-30 ${
        sidebarVisible ? 'w-80' : 'w-0 overflow-hidden lg:w-0'
      } lg:relative fixed h-full lg:h-auto`} id="chat-sidebar">
        <ThreadList
          threads={threads}
          currentId={currentId}
          onSelect={(id) => {
            setCurrentId(id);
            // Close sidebar on mobile after selection
            if (window.innerWidth < 1024) {
              setSidebarVisible(false);
            }
          }}
          onCreate={handleCreateThread}
        />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              onClick={() => setSidebarVisible(!sidebarVisible)}
              title={sidebarVisible ? "Hide conversations" : "Show conversations"}
            >
              {sidebarVisible ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              )}
            </button>
            <div className="h-6 w-px bg-gray-300" />
            <h1 className="text-lg font-semibold text-gray-900">
              {loading ? "Loading…" : currentId ? "Chat Assistant" : "Start a conversation"}
            </h1>
          </div>
          <button
            onClick={handleCreateThread}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span className="hidden sm:inline">New chat</span>
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-hidden">
          <MessagePane messages={currentMsgs} />
        </div>
        
        {/* Input area */}
        <MessageInput onSend={handleSend} disabled={!currentId || sending} />
      </div>
    </div>
  );
}