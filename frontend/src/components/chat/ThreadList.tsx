import type { ChatThread } from "@/services/chat";

type Props = {
  threads: ChatThread[];
  currentId: string | number | null;
  onSelect: (id: string | number) => void;
  onCreate: () => void;
};

export default function ThreadList({ threads, currentId, onSelect, onCreate }: Props) {
  console.log("ThreadList rendered with threads:", threads.length);
  
  const handleCreateClick = () => {
    console.log("New button clicked!");
    onCreate();
  };
  
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-900">Conversations</h2>
          <span className="text-xs text-gray-500">{threads.length}</span>
        </div>
        <button
          onClick={handleCreateClick}
          className="w-full flex items-center gap-3 p-3 rounded-lg border-2 border-dashed border-gray-300 text-gray-600 hover:border-gray-400 hover:bg-gray-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="text-sm font-medium">New conversation</span>
        </button>
      </div>

      {/* Threads list */}
      <div className="flex-1 overflow-y-auto p-3">
        {threads.length === 0 ? (
          <div className="p-6 text-center">
            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="text-sm text-gray-500">No conversations yet</p>
            <p className="text-xs text-gray-400 mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {threads.map((t) => (
              <button
                key={t.id}
                onClick={() => onSelect(t.id)}
                className={`w-full text-left p-3 rounded-lg transition-all duration-150 group ${
                  currentId === t.id 
                    ? "bg-blue-50 border border-blue-200 text-blue-900 shadow-sm" 
                    : "text-gray-700 hover:bg-white hover:shadow-sm border border-transparent"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate mb-1">
                      {t.title || `Conversation ${t.id}`}
                    </div>
                    <div className="text-xs text-gray-500">
                      {t.updated_at ? new Date(t.updated_at).toLocaleDateString() : "New chat"}
                    </div>
                  </div>
                  <div className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
