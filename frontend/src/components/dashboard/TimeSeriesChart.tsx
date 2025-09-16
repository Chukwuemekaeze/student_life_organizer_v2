// src/components/dashboard/TimeSeriesChart.tsx
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

// Color palette for different metrics
const colors = {
  journal_create: "#10b981", // Green
  chat_query: "#3b82f6",     // Blue  
  calendar_sync: "#f59e0b",  // Orange
  notes_sync: "#8b5cf6",     // Purple
};

// Format date for display
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  });
};

// Format metric names for display
const formatMetricName = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        <p className="font-medium text-gray-900 mb-2">{formatDate(label)}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {formatMetricName(entry.dataKey)}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function TimeSeriesChart({ data, keys, height = 280 }: { data: Array<{ t: string; [k: string]: any }>; keys: string[]; height?: number }) {
  // Flatten nested counts to top-level keys for Recharts
  const flat = data.map((p) => ({ 
    t: p.t, 
    displayDate: formatDate(p.t),
    ...(p.counts || p) 
  }));
  
  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={flat} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis 
            dataKey="displayDate" 
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickLine={{ stroke: '#d1d5db' }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            allowDecimals={false} 
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickLine={{ stroke: '#d1d5db' }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            formatter={(value) => formatMetricName(value)}
            wrapperStyle={{ fontSize: '12px' }}
          />
          {keys.map((k) => (
            <Line 
              key={k} 
              type="monotone" 
              dataKey={k} 
              stroke={colors[k as keyof typeof colors] || '#6b7280'}
              strokeWidth={2}
              dot={{ fill: colors[k as keyof typeof colors] || '#6b7280', strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5, stroke: colors[k as keyof typeof colors] || '#6b7280', strokeWidth: 2 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
