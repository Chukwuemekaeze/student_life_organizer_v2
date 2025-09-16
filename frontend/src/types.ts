export type Journal = { 
  id: number; 
  content: string; 
  created_at: string; 
  updated_at: string; 
};

export type CalendarEvent = {
  id: string | number;
  title: string;
  start_time: string; // ISO
  end_time: string;   // ISO
  status?: string | null;
  html_link?: string | null;
  location?: string | null;
  description?: string | null;
  is_all_day?: boolean;
};

