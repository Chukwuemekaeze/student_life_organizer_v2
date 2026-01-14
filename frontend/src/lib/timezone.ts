// Timezone utility for Nigeria (West Africa Time - UTC+1)
const NIGERIA_TIMEZONE_OFFSET = 1; // UTC+1
const NIGERIA_TIMEZONE = 'Africa/Lagos'; // IANA timezone for Nigeria

/**
 * Convert a UTC datetime string to Nigeria local time for display
 */
export function formatNigeriaTime(utcDateString: string | null | undefined): string {
  if (!utcDateString) return '—';
  
  try {
    const date = new Date(utcDateString);
    
    // Use Intl.DateTimeFormat for proper timezone handling
    return new Intl.DateTimeFormat('en-US', {
      timeZone: NIGERIA_TIMEZONE,
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  } catch (e) {
    console.warn(`Failed to format Nigeria time: ${utcDateString}`, e);
    return utcDateString || '—';
  }
}

/**
 * Format just the date portion in Nigeria timezone
 */
export function formatNigeriaDate(utcDateString: string | null | undefined): string {
  if (!utcDateString) return '—';
  
  try {
    const date = new Date(utcDateString);
    
    return new Intl.DateTimeFormat('en-US', {
      timeZone: NIGERIA_TIMEZONE,
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  } catch (e) {
    console.warn(`Failed to format Nigeria date: ${utcDateString}`, e);
    return utcDateString || '—';
  }
}

/**
 * Format just the time portion in Nigeria timezone
 */
export function formatNigeriaTimeOnly(utcDateString: string | null | undefined): string {
  if (!utcDateString) return '—';
  
  try {
    const date = new Date(utcDateString);
    
    return new Intl.DateTimeFormat('en-US', {
      timeZone: NIGERIA_TIMEZONE,
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  } catch (e) {
    console.warn(`Failed to format Nigeria time only: ${utcDateString}`, e);
    return utcDateString || '—';
  }
}

/**
 * Convert a local datetime-local input value to UTC ISO string
 * Assumes the input is in Nigeria timezone
 */
export function nigeriaLocalToUTC(localDatetimeString: string): string {
  if (!localDatetimeString) return '';
  
  try {
    // Parse the local datetime string as if it's in Nigeria timezone
    const localDate = new Date(localDatetimeString);
    
    // Adjust for Nigeria timezone offset (subtract 1 hour to get UTC)
    const utcDate = new Date(localDate.getTime() - (NIGERIA_TIMEZONE_OFFSET * 60 * 60 * 1000));
    
    return utcDate.toISOString();
  } catch (e) {
    console.warn(`Failed to convert Nigeria local to UTC: ${localDatetimeString}`, e);
    return '';
  }
}

/**
 * Convert a UTC ISO string to local datetime-local input format
 * Converts to Nigeria timezone
 */
export function utcToNigeriaLocal(utcIsoString: string): string {
  if (!utcIsoString) return '';
  
  try {
    const utcDate = new Date(utcIsoString);
    
    // Add Nigeria timezone offset (add 1 hour from UTC)
    const nigeriaDate = new Date(utcDate.getTime() + (NIGERIA_TIMEZONE_OFFSET * 60 * 60 * 1000));
    
    // Format as datetime-local input expects (YYYY-MM-DDTHH:mm)
    return nigeriaDate.toISOString().slice(0, 16);
  } catch (e) {
    console.warn(`Failed to convert UTC to Nigeria local: ${utcIsoString}`, e);
    return '';
  }
}

/**
 * Get current Nigeria time as ISO string
 */
export function getCurrentNigeriaTime(): string {
  const now = new Date();
  const nigeriaTime = new Date(now.getTime() + (NIGERIA_TIMEZONE_OFFSET * 60 * 60 * 1000));
  return nigeriaTime.toISOString();
}

/**
 * Get current Nigeria date for date range calculations
 */
export function getCurrentNigeriaDate(): string {
  const now = new Date();
  
  // Get Nigeria date using Intl.DateTimeFormat
  const nigeriaDate = new Intl.DateTimeFormat('sv-SE', { // 'sv-SE' gives YYYY-MM-DD format
    timeZone: NIGERIA_TIMEZONE
  }).format(now);
  
  return nigeriaDate;
}

/**
 * Check if a date is overdue (past current Nigeria time)
 */
export function isOverdue(dueDateUTC: string | null): boolean {
  if (!dueDateUTC) return false;
  
  try {
    const dueDate = new Date(dueDateUTC);
    const now = new Date();
    
    return dueDate.getTime() < now.getTime();
  } catch (e) {
    return false;
  }
}

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days") in Nigeria context
 */
export function formatRelativeTime(utcDateString: string | null | undefined): string {
  if (!utcDateString) return '—';
  
  try {
    const date = new Date(utcDateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else if (diffSeconds > 0) {
      return `${diffSeconds} second${diffSeconds > 1 ? 's' : ''} ago`;
    } else {
      return 'just now';
    }
  } catch (e) {
    return utcDateString || '—';
  }
}



