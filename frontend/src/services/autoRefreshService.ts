// src/services/autoRefreshService.ts
import { eventBus } from '../lib/eventBus';
import * as tasksService from './tasks';
import * as dashboardService from './dashboard';
import * as notificationsService from './notifications';

// Types for refresh handlers
type RefreshHandler = () => Promise<void> | void;

export class AutoRefreshService {
  private refreshHandlers: Map<string, RefreshHandler> = new Map();
  private initialized = false;

  // Initialize the auto-refresh service
  init() {
    if (this.initialized) return;
    
    console.log('[AutoRefreshService] Initializing auto-refresh...');

    // Helper function to check if we should skip refresh
    const shouldSkipRefresh = () => {
      // Skip on chat page
      if (window.location.pathname === '/chat') {
        console.log('[AutoRefreshService] Skipping refresh - on chat page');
        return true;
      }
      return false;
    };
    
    // Listen for calendar changes
    eventBus.on('calendar-changed', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('calendar');
      }
    });

    // Listen for task changes
    eventBus.on('task-changed', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('tasks');
      }
    });

    // Listen for journal changes
    eventBus.on('journal-changed', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('journal');
      }
    });

    // Listen for notification changes
    eventBus.on('notification-changed', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('notifications');
      }
    });

    // Listen for notes changes
    eventBus.on('notes-changed', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('notes');
      }
    });

    // Listen for dashboard data becoming stale
    eventBus.on('dashboard-data-stale', () => {
      if (!shouldSkipRefresh()) {
        this.runRefreshHandler('dashboard');
      }
    });

    // Listen for any agent tool execution
    eventBus.on('agent-tool-executed', (data) => {
      if (!shouldSkipRefresh()) {
        // Trigger refresh for all relevant data types
        console.log('[AutoRefreshService] Agent tool executed:', data.tool);
        this.runRefreshHandler('dashboard');
        this.runRefreshHandler('notifications');
      }
    });

    this.initialized = true;
  }

  // Register a refresh handler for a specific data type
  registerRefreshHandler(key: string, handler: RefreshHandler) {
    this.refreshHandlers.set(key, handler);
    console.log(`[AutoRefreshService] Registered refresh handler for: ${key}`);
  }

  // Unregister a refresh handler
  unregisterRefreshHandler(key: string) {
    this.refreshHandlers.delete(key);
    console.log(`[AutoRefreshService] Unregistered refresh handler for: ${key}`);
  }

  // Run a specific refresh handler
  private async runRefreshHandler(key: string) {
    const handler = this.refreshHandlers.get(key);
    if (handler) {
      try {
        await handler();
        console.log(`[AutoRefreshService] Refreshed: ${key}`);
      } catch (error) {
        console.error(`[AutoRefreshService] Error refreshing ${key}:`, error);
      }
    }
  }

  // Manual trigger for specific data types
  triggerRefresh(key: string) {
    this.runRefreshHandler(key);
  }

  // Cleanup
  cleanup() {
    this.refreshHandlers.clear();
    this.initialized = false;
  }
}

// Global singleton instance
export const autoRefreshService = new AutoRefreshService();
