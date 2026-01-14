// src/hooks/useAutoRefresh.ts
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { eventBus, type AppEventType } from '../lib/eventBus';

type RefreshCallback = () => void | Promise<void>;

// Global state to track if user is actively writing
let isUserWriting = false;
let writeActivityTimeout: NodeJS.Timeout | null = null;

// Function to set writing state
export function setUserWriting(writing: boolean) {
  isUserWriting = writing;
  
  // Clear existing timeout
  if (writeActivityTimeout) {
    clearTimeout(writeActivityTimeout);
    writeActivityTimeout = null;
  }
  
  // If user started writing, set a timeout to automatically clear the state
  if (writing) {
    writeActivityTimeout = setTimeout(() => {
      isUserWriting = false;
      console.log('[AutoRefresh] User writing timeout - re-enabling auto-refresh');
    }, 30000); // 30 seconds of inactivity clears the writing state
  }
  
  console.log(`[AutoRefresh] User writing state: ${writing}`);
}

export function useAutoRefresh(
  events: AppEventType | AppEventType[],
  refreshCallback: RefreshCallback,
  enabled: boolean = true
) {
  const callbackRef = useRef(refreshCallback);
  const location = useLocation();
  
  // Keep callback ref updated
  useEffect(() => {
    callbackRef.current = refreshCallback;
  }, [refreshCallback]);

  useEffect(() => {
    if (!enabled) return;

    // Completely disable auto-refresh on chat page
    if (location.pathname === '/chat') {
      console.log('[AutoRefresh] Disabled on chat page');
      return;
    }

    const eventList = Array.isArray(events) ? events : [events];
    const unsubscribers: (() => void)[] = [];

    // Subscribe to all specified events
    eventList.forEach(event => {
      const unsubscribe = eventBus.on(event, async (data) => {
        // Don't refresh if user is actively writing
        if (isUserWriting) {
          console.log(`[AutoRefresh] Skipping refresh for ${event} - user is writing`);
          return;
        }
        
        // Don't refresh on chat page
        if (window.location.pathname === '/chat') {
          console.log(`[AutoRefresh] Skipping refresh for ${event} - on chat page`);
          return;
        }

        try {
          await callbackRef.current();
          console.log(`[useAutoRefresh] Refreshed data for event: ${event}`);
        } catch (error) {
          console.error(`[useAutoRefresh] Error refreshing data for ${event}:`, error);
        }
      });
      unsubscribers.push(unsubscribe);
    });

    // Cleanup subscriptions
    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [events, enabled, location.pathname]);
}

// Hook for cross-component updates
export function useDataInvalidation() {
  const triggerRefresh = {
    calendar: (data?: any) => eventBus.emit('calendar-changed', data),
    tasks: (data?: any) => eventBus.emit('task-changed', data),
    journal: (data?: any) => eventBus.emit('journal-changed', data),
    notifications: (data?: any) => eventBus.emit('notification-changed', data),
    notes: (data?: any) => eventBus.emit('notes-changed', data),
    dashboard: (data?: any) => eventBus.emit('dashboard-data-stale', data),
    agentToolExecuted: (data?: any) => eventBus.emit('agent-tool-executed', data),
  };

  return triggerRefresh;
}
