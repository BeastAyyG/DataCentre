import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface TimeSeriesChartProps {
  data: { ts: string; baseline: number; scenario?: number }[];
  dataKey1?: string;
  dataKey2?: string;
  color1?: string;
  color2?: string;
  height?: number;
  yLabel?: string;
}

export function TimeSeriesChart({
  data,
  dataKey1 = 'baseline',
  dataKey2 = 'scenario',
  color1 = '#3b82f6',
  color2 = '#22c55e',
  height = 240,
  yLabel,
}: TimeSeriesChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="ts"
          tickFormatter={(v) => format(new Date(v), 'HH:mm')}
          stroke="#94a3b8"
          fontSize={11}
        />
        <YAxis stroke="#94a3b8" fontSize={11} label={yLabel ? { value: yLabel, angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 } : undefined} />
        <Tooltip
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: 12 }}
          labelFormatter={(v) => format(new Date(v), 'MMM d, HH:mm')}
        />
        <Area type="monotone" dataKey={dataKey1} stroke={color1} fill={color1} fillOpacity={0.2} strokeWidth={2} />
        {dataKey2 && <Area type="monotone" dataKey={dataKey2} stroke={color2} fill={color2} fillOpacity={0.2} strokeWidth={2} />}
      </AreaChart>
    </ResponsiveContainer>
  );
}
