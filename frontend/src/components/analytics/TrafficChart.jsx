import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function TrafficChart({ data }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 h-full">
      <h2 className="text-slate-400 text-sm mb-4">Customer Traffic</h2>
      {data.length === 0 ? (
        <p className="text-slate-500 text-sm">No data yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip
              contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }}
            />
            <Line
              type="monotone"
              dataKey="visitors"
              stroke="rgb(16,185,129)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
