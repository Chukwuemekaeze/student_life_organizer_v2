export type ToolTrace = {
  tool: string;
  result?: unknown;
  error?: string;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: number;
  tools?: ToolTrace[];
};

