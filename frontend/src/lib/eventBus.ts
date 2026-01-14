// src/lib/eventBus.ts
type EventCallback = (data?: any) => void;

export type AppEventType = 
  | 'calendar-changed'
  | 'task-changed' 
  | 'journal-changed'
  | 'notification-changed'
  | 'notes-changed'
  | 'agent-tool-executed'
  | 'dashboard-data-stale';

class EventBus {
  private listeners: Record<AppEventType, Set<EventCallback>> = {
    'calendar-changed': new Set(),
    'task-changed': new Set(),
    'journal-changed': new Set(),
    'notification-changed': new Set(),
    'notes-changed': new Set(),
    'agent-tool-executed': new Set(),
    'dashboard-data-stale': new Set(),
  };

  // Subscribe to an event
  on(event: AppEventType, callback: EventCallback): () => void {
    this.listeners[event].add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners[event].delete(callback);
    };
  }

  // Emit an event to all subscribers
  emit(event: AppEventType, data?: any): void {
    console.log(`[EventBus] Emitting event: ${event}`, data);
    this.listeners[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`[EventBus] Error in event listener for ${event}:`, error);
      }
    });
  }

  // One-time event listener
  once(event: AppEventType, callback: EventCallback): void {
    const unsubscribe = this.on(event, (data) => {
      callback(data);
      unsubscribe();
    });
  }
}

export const eventBus = new EventBus();

