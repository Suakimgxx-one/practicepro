import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PieceProgressPoint } from "@/types/piece";

export function ProgressChart({ progress }: { progress: PieceProgressPoint[] }) {
  const chartData = progress
    .filter((p) => p.mean_absolute_cents_deviation !== null)
    .map((p, i) => ({
      attempt: i + 1,
      cents: p.mean_absolute_cents_deviation as number,
      date: new Date(p.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    }));

  if (chartData.length === 0) {
    return <p className="text-sm text-ink-500 py-2">Progress appears here once you've compared at least one practice attempt.</p>;
  }
  if (chartData.length === 1) {
    return (
      <p className="text-sm text-ink-300 py-2">
        One attempt so far — {chartData[0].cents.toFixed(1)} cents average deviation. Log another attempt to start seeing a trend.
      </p>
    );
  }
  return (
    <div>
      <p className="text-xs text-ink-500 mb-2">Pitch accuracy across attempts (lower is closer to the reference)</p>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
          <XAxis dataKey="date" stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} width={36} />
          <Tooltip
            contentStyle={{ background: "#191B24", border: "1px solid #2E313F", borderRadius: 8, fontSize: 12, fontFamily: "Plus Jakarta Sans" }}
            formatter={(value: number) => [`${value.toFixed(1)} cents`, "avg deviation"]}
          />
          <Line type="monotone" dataKey="cents" stroke="#9C8CFF" strokeWidth={1.75} dot={{ r: 3, fill: "#9C8CFF" }} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
