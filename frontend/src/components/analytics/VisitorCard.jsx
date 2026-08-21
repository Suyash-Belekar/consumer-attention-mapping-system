export default function VisitorCard({ count }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 flex flex-col justify-center">
      <span className="text-slate-400 text-sm">Visitors Right Now</span>
      <span className="text-4xl font-semibold mt-2">
        {count === null ? "—" : count}
      </span>
    </div>
  );
}
