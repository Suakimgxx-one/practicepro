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
    return (
      <p className="text-sm text-ink-faint py-2">
        Progress appears here once you've compared at least one practice attempt.
      </p>
    );
  }

  if (chartData.length === 1) {
    return (
      <p className="text-sm text-ink-soft py-2">
        One attempt so far — {chartData[0].cents.toFixed(1)} cents average deviation. Log another
        attempt to start seeing a trend.
      </p>
    );
  }

  return (
    <div>
      <p className="text-xs text-ink-faint mb-2">Pitch accuracy across attempts (lower is closer to the reference)</p>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
          <XAxis dataKey="date" stroke="#A69B8A" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#A69B8A" fontSize={11} tickLine={false} axisLine={false} width={36} />
          <Tooltip
            contentStyle={{ background: "#FAF7F0", border: "1px solid #DDD5C7", borderRadius: 4, fontSize: 12, fontFamily: "IBM Plex Sans" }}
            formatter={(value: number) => [`${value.toFixed(1)} cents`, "avg deviation"]}
          />
          <Line type="monotone" dataKey="cents" stroke="#A67C3D" strokeWidth={1.75} dot={{ r: 3, fill: "#A67C3D" }} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
