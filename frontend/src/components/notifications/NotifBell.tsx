import { useEffect, useRef } from "react";
import { useAtom } from "jotai";
import { Bell } from "lucide-react";
import { unreadCountAtom, unreadItemsAtom, notifOpenAtom } from "../../state/notificationsAtoms";
import { fetchUnread, markRead, scanDue } from "../../services/notifications";
import { useNavigate } from "react-router-dom";

export default function NotifBell() {
  const [count, setCount] = useAtom(unreadCountAtom);
  const [items, setItems] = useAtom(unreadItemsAtom);
  const [open, setOpen] = useAtom(notifOpenAtom);
  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  async function refresh() {
    try {
      const out = await fetchUnread();
      setItems(out.items);
      setCount(out.count);
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => {
    // Dev convenience: ask backend to scan on first mount
    scanDue().finally(refresh);
    const t = setInterval(refresh, 60000); // 60s
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Node;
      // Don't close if clicking on the button or inside the dropdown
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(target) && 
        buttonRef.current && 
        !buttonRef.current.contains(target)
      ) {
        setOpen(false);
      }
    }

    if (open) {
      // Use a small delay to avoid conflicts with the button click
      const timer = setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
      }, 100);
      
      return () => {
        clearTimeout(timer);
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [open, setOpen]);

  async function onItemClick(id: number, ref_type?: string | null, ref_id?: number | null) {
    await markRead([id]);
    refresh();
    setOpen(false); // Close dropdown when item is clicked
    if (ref_type === "task" && ref_id) {
      navigate("/tasks");
    }
  }

  function handleToggle() {
    setOpen(!open);
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        ref={buttonRef}
        onClick={handleToggle}
        className="w-full flex items-center justify-between rounded-md px-3 py-2 text-sm transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300"
      >
        <div className="flex items-center gap-2">
          <Bell size={18} />
          <span>Notifications</span>
        </div>
        {count > 0 && (
          <span className="bg-red-500 text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center font-medium">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute left-0 mt-2 w-80 bg-white border rounded-lg shadow-lg z-50">
          <div className="px-4 py-3 text-sm font-medium border-b bg-gray-50">
            Notifications
          </div>
          <div className="max-h-80 overflow-auto">
            {items.length === 0 ? (
              <div className="p-4 text-sm text-gray-500 text-center">
                No new notifications
              </div>
            ) : (
              items.map((n) => (
                <button 
                  key={n.id} 
                  onClick={() => onItemClick(n.id, n.ref_type, n.ref_id)} 
                  className="w-full text-left p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
                >
                  <div className="text-sm font-medium text-gray-900 mb-1">{n.title}</div>
                  <div className="text-xs text-gray-600 line-clamp-2">{n.body}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(n.created_at).toLocaleDateString()}
                  </div>
                </button>
              ))
            )}
          </div>
          {items.length > 0 && (
            <div className="px-4 py-3 border-t bg-gray-50">
              <button 
                className="text-xs text-blue-600 hover:text-blue-800 underline font-medium" 
                onClick={async () => { 
                  await markRead(items.map(i => i.id)); 
                  refresh();
                  setOpen(false); // Close dropdown after marking all read
                }}
              >
                Mark all read
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
