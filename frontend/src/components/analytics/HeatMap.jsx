// Renders zone attention intensity as an SVG scatter, avoiding an extra
// dependency. Swap for react-heatmap-grid if you want a grid-cell look
// instead of point intensity.
export default function HeatMap({ points }) {
  const maxValue = Math.max(1, ...points.map((p) => p.value));
  const width = 640;
  const height = 360;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="text-slate-400 text-sm mb-4">Customer Attention Heatmap</h2>
      {points.length === 0 ? (
        <p className="text-slate-500 text-sm">No data yet.</p>
      ) : (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          <rect width={width} height={height} rx={8} fill="#0f172a" />
          {points.map((p, i) => {
            const intensity = p.value / maxValue;
            const radius = 10 + intensity * 28;
            return (
              <circle
                key={i}
                cx={(p.x / 1000) * width}
                cy={(p.y / 1000) * height}
                r={radius}
                fill="rgb(16,185,129)"
                opacity={0.15 + intensity * 0.5}
              />
            );
          })}
        </svg>
      )}
      <p className="text-slate-500 text-xs mt-2">
        Point size/opacity = cumulative attention time per zone
      </p>
    </div>
  );
}
