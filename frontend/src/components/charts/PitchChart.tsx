import {
  Line,
  LineChart,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PitchResultData } from "@/types/analysis";
import { formatTime } from "@/lib/formatTime";

export function PitchChart({ data }: { data: PitchResultData }) {
  const chartData = data.points.map((p) => ({ time: p.reference_time, cents: p.cents_deviation }));

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-medium text-ink-300">Pitch</h3>
        <span className="text-xs text-ink-500">{data.mean_absolute_cents_deviation.toFixed(1)} cents average deviation</span>
      </div>
      {chartData.length === 0 ? (
        <p className="text-sm text-ink-500 py-6">No voiced pitch data was found to compare.</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
            {data.flagged_regions.map((region, i) => (
              <ReferenceArea key={i} x1={region.start} x2={region.end} fill="#F87171" fillOpacity={0.1} strokeOpacity={0} />
            ))}
            <ReferenceLine y={0} stroke="#2E313F" />
            <XAxis dataKey="time" type="number" domain={["dataMin", "dataMax"]} tickFormatter={formatTime} stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} width={36} />
            <Tooltip
              contentStyle={{ background: "#191B24", border: "1px solid #2E313F", borderRadius: 8, fontSize: 12, fontFamily: "Plus Jakarta Sans" }}
              labelFormatter={(t) => formatTime(Number(t))}
              formatter={(value: number) => [`${value.toFixed(1)} cents`, "deviation"]}
            />
            <Line type="monotone" dataKey="cents" stroke="#9C8CFF" dot={false} strokeWidth={1.75} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
