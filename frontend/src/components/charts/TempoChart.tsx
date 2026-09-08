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
import type { TempoResultData } from "@/types/analysis";
import { formatTime } from "@/lib/formatTime";

export function TempoChart({ data }: { data: TempoResultData }) {
  const chartData = data.points.map((p) => ({ time: p.reference_time, ratio: p.local_tempo_ratio }));

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-medium text-ink-300">Tempo</h3>
        <span className="text-xs text-ink-500">
          {data.reference_average_bpm && data.student_average_bpm
            ? `${Math.round(data.reference_average_bpm)} vs ${Math.round(data.student_average_bpm)} bpm`
            : "BPM estimate unavailable"}
        </span>
      </div>
      {chartData.length === 0 ? (
        <p className="text-sm text-ink-500 py-6">Not enough data to chart a tempo curve.</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
            {data.flagged_regions.map((region, i) => (
              <ReferenceArea key={i} x1={region.start} x2={region.end} fill={region.label === "dragging" ? "#FBBF24" : "#34D399"} fillOpacity={0.1} strokeOpacity={0} />
            ))}
            <ReferenceLine y={1.0} stroke="#2E313F" />
            <XAxis dataKey="time" type="number" domain={["dataMin", "dataMax"]} tickFormatter={formatTime} stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#5A5D6E" fontSize={11} domain={["auto", "auto"]} tickLine={false} axisLine={false} width={32} />
            <Tooltip
              contentStyle={{ background: "#191B24", border: "1px solid #2E313F", borderRadius: 8, fontSize: 12, fontFamily: "Plus Jakarta Sans" }}
              labelFormatter={(t) => formatTime(Number(t))}
              formatter={(value: number) => [value.toFixed(2), "pace ratio"]}
            />
            <Line type="monotone" dataKey="ratio" stroke="#34D399" dot={false} strokeWidth={1.75} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
