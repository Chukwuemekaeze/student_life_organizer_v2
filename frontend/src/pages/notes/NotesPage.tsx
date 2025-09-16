// src/pages/notes/NotesPage.tsx
import { useEffect, useState } from "react";
import { useAtom } from "jotai";
import { toast } from "sonner";
import {
  getNotesStatus,
  connectNotes,
  disconnectNotes,
  syncNotes,
  listNotes,
  type NoteItem,
} from "../../services/notes";
import { notesAtom, notesLoadingAtom, notesConnectedAtom } from "../../state/notesAtoms";

export default function NotesPage() {
  const [notes, setNotes] = useAtom(notesAtom);
  const [loading, setLoading] = useAtom(notesLoadingAtom);
  const [connected, setConnected] = useAtom(notesConnectedAtom);
  const [initialized, setInitialized] = useState(false);
  const [notionToken, setNotionToken] = useState("");
  const [showTokenInput, setShowTokenInput] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const status = await getNotesStatus();
        setConnected(status.connected);
        if (status.connected) {
          const data = await listNotes({ limit: 10 });
          setNotes(data.items);
        } else {
          setNotes([]);
        }
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load notes");
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    })();
  }, [setConnected, setLoading, setNotes]);

  async function onConnect() {
    if (!notionToken.trim()) {
      toast.error("Please enter a Notion token");
      return;
    }

    try {
      setLoading(true);
      await connectNotes(notionToken.trim());
      setConnected(true);
      setShowTokenInput(false);
      setNotionToken("");
      
      // Fetch notes after connecting
      const data = await listNotes({ limit: 10 });
      setNotes(data.items);
      
      toast.success("Connected to Notion");
    } catch (e: any) {
      console.error(e);
      toast.error("Unable to connect to Notion. Please check your token.");
    } finally {
      setLoading(false);
    }
  }

  async function onDisconnect() {
    try {
      setLoading(true);
      await disconnectNotes();
      setConnected(false);
      setNotes([]);
      toast.success("Disconnected from Notion");
    } catch (e: any) {
      console.error(e);
      toast.error("Failed to disconnect");
    } finally {
      setLoading(false);
    }
  }

  async function onSync() {
    try {
      setLoading(true);
      await syncNotes();
      const data = await listNotes({ limit: 10 });
      setNotes(data.items);
      toast.success("Notes synced");
    } catch (e: any) {
      console.error(e);
      toast.error("Sync failed");
    } finally {
      setLoading(false);
    }
  }

  const hasNotes = !!notes && notes.length > 0;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Notes</h1>
        <div className="flex items-center gap-2">
          {connected ? (
            <>
              <button
                onClick={onSync}
                disabled={loading}
                className="px-3 py-1.5 rounded-md bg-black text-white disabled:opacity-50"
              >
                {loading ? "Syncing…" : "Sync"}
              </button>
              <button
                onClick={onDisconnect}
                disabled={loading}
                className="px-3 py-1.5 rounded-md border border-neutral-300 disabled:opacity-50"
              >
                Disconnect
              </button>
            </>
          ) : (
            <button
              onClick={() => setShowTokenInput(true)}
              disabled={loading}
              className="px-3 py-1.5 rounded-md bg-black text-white disabled:opacity-50"
            >
              Connect Notion
            </button>
          )}
        </div>
      </div>

      {showTokenInput && !connected && (
        <div className="rounded-lg border p-4 space-y-4">
          <h3 className="font-medium">Connect to Notion</h3>
          <p className="text-sm text-gray-600">
            Enter your Notion integration token. You can create one at{" "}
            <a 
              href="https://www.notion.so/my-integrations" 
              target="_blank" 
              rel="noreferrer"
              className="underline"
            >
              notion.so/my-integrations
            </a>
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={notionToken}
              onChange={(e) => setNotionToken(e.target.value)}
              placeholder="Enter Notion integration token"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              disabled={loading}
            />
            <button
              onClick={onConnect}
              disabled={loading || !notionToken.trim()}
              className="px-4 py-2 rounded-md bg-black text-white disabled:opacity-50"
            >
              {loading ? "Connecting…" : "Connect"}
            </button>
            <button
              onClick={() => {
                setShowTokenInput(false);
                setNotionToken("");
              }}
              disabled={loading}
              className="px-4 py-2 rounded-md border border-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {!initialized ? (
        <div className="text-sm text-neutral-500">Loading…</div>
      ) : !connected ? (
        <div className="rounded-lg border border-dashed p-6 text-neutral-600">
          Connect your Notion account to see your latest notes here.
        </div>
      ) : hasNotes ? (
        <ul className="divide-y rounded-lg border">
          {notes!.map((n: NoteItem) => (
            <li key={n.page_id} className="p-4 flex items-start justify-between gap-4">
              <div>
                <div className="font-medium">{n.title || "Untitled"}</div>
                {n.last_edited_time && (
                  <div className="text-xs text-neutral-500">
                    Last edited: {new Date(n.last_edited_time).toLocaleString()}
                  </div>
                )}
              </div>
              {n.url && (
                <a
                  href={n.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm underline"
                >
                  Open
                </a>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <div className="rounded-lg border p-6 text-neutral-600">
          No notes found. Try Sync to fetch your latest Notion pages.
        </div>
      )}
    </div>
  );
}


