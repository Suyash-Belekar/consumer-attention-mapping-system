import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function ShelfAttentionChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { shelf_name: "Shelf A", total_dwell_seconds: 42.5, customers: 8 },
    { shelf_name: "Shelf B", total_dwell_seconds: 88.0, customers: 14 },
    { shelf_name: "Beverages", total_dwell_seconds: 64.2, customers: 11 },
    { shelf_name: "Snacks", total_dwell_seconds: 31.0, customers: 5 },
  ];

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/90 backdrop-blur p-6 shadow-xl h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-emerald-400 font-semibold text-base tracking-wide">
            Shelf Viewing Duration
          </h2>
          <p className="text-slate-400 text-xs mt-0.5">
            Active attention seconds accumulated today
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 font-medium">
          Live AI Stream
        </span>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="shelf_name"
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            unit="s"
          />
          <Tooltip
            cursor={{ fill: "rgba(30, 41, 59, 0.5)" }}
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "0.75rem",
              color: "#f8fafc",
              fontSize: "0.85rem",
            }}
            formatter={(value) => [`${value}s`, "Dwell Time"]}
            labelFormatter={(label) => `Zone: ${label}`}
          />
          <Bar
            dataKey="total_dwell_seconds"
            fill="url(#emeraldGradient)"
            radius={[6, 6, 0, 0]}
          />
          <defs>
            <linearGradient id="emeraldGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
              <stop offset="100%" stopColor="#059669" stopOpacity={0.7} />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
