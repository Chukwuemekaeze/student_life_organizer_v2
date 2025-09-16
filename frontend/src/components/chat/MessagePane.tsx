import type { ChatMessage } from "@/services/chat";

type Props = { messages: ChatMessage[] };

export default function MessagePane({ messages }: Props) {
  return (
    <div className="flex-1 overflow-y-auto">
      {messages.length === 0 ? (
        <div className="h-full flex items-center justify-center">
          <div className="text-center max-w-md mx-auto px-4">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Start a conversation</h3>
            <p className="text-gray-500 text-sm">Ask me anything about your studies, tasks, or life organization!</p>
          </div>
        </div>
      ) : (
        <div className="max-w-3xl mx-auto">
          {messages.map((m) => (
            <div key={m.id} className={`group ${m.role === "assistant" ? "bg-gray-50" : "bg-white"}`}>
              <div className="px-4 py-6 sm:px-6">
                <div className="flex gap-4">
                  {/* Avatar */}
                  <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    m.role === "assistant" 
                      ? "bg-green-600 text-white" 
                      : "bg-blue-600 text-white"
                  }`}>
                    {m.role === "assistant" ? "AI" : "U"}
                  </div>
                  
                  {/* Message content */}
                  <div className="flex-1 min-w-0">
                    <div className={`prose prose-sm max-w-none ${
                      m.role === "assistant" ? "prose-gray" : "prose-blue"
                    }`}>
                      <div className="whitespace-pre-wrap break-words text-gray-900 leading-relaxed">
                        {m.content}
                      </div>
                    </div>
                    
                    {/* Timestamp */}
                    <div className="mt-2 text-xs text-gray-400">
                      {m.created_at ? new Date(m.created_at).toLocaleTimeString() : ""}
                    </div>
                  </div>
                  
                  {/* Action buttons - show on hover */}
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
