export default function ProductRanking({ products }) {
  const maxScore = Math.max(1, ...products.map((p) => p.score));

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="text-slate-400 text-sm mb-4">Top Products by Attention</h2>
      {products.length === 0 ? (
        <p className="text-slate-500 text-sm">No data yet.</p>
      ) : (
        <ul className="space-y-3">
          {products.map((p) => (
            <li key={p.product}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium">{p.product}</span>
                <span className="text-slate-400">
                  {p.customers} customers · {p.avg_dwell_seconds}s avg
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-emerald-500"
                  style={{ width: `${(p.score / maxScore) * 100}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
