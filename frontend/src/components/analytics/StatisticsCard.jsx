import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function StatisticsCard({ title, value, subtitle }) {
  return (
    <Card className="rounded-3xl border border-slate-800 bg-slate-950 p-5">
      <CardHeader className="p-0 mb-3">
        <CardTitle className="text-sm font-medium text-slate-400">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <p className="text-4xl font-semibold text-white">{value}</p>
        {subtitle && <p className="mt-2 text-sm text-slate-500">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}
