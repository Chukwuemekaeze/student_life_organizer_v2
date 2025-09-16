// src/lib/date.ts
export function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function rangeFromWindow(windowDays: number): { from: string; to: string } {
  const to = new Date();
  const from = new Date();
  from.setDate(to.getDate() - (windowDays - 1));
  return { from: isoDate(from), to: isoDate(to) };
}
