import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function RecommendationCard({ priority, message }) {
  return (
    <Card className="rounded-3xl border border-slate-800 bg-slate-950 p-5">
      <CardHeader className="p-0 mb-3">
        <CardTitle className="text-sm font-medium text-slate-400">
          Recommendation
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="mb-2 text-xs uppercase tracking-[0.2em] text-emerald-400">
          {priority}
        </div>
        <p className="text-sm text-slate-200">{message}</p>
      </CardContent>
    </Card>
  );
}
