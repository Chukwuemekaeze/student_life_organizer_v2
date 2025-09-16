export function fmt(dt: string | Date) {
  const d = typeof dt === 'string' ? new Date(dt) : dt;
  return d.toLocaleString();
}

