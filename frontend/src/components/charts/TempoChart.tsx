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

interface TempoChartProps {
  data: TempoResultData;
}

export function TempoChart({ data }: TempoChartProps) {
  const chartData = data.points.map((p) => ({ time: p.reference_time, ratio: p.local_tempo_ratio }));

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-medium text-ink-soft">Tempo</h3>
        <span className="text-xs text-ink-faint">
          {data.reference_average_bpm && data.student_average_bpm
            ? `${Math.round(data.reference_average_bpm)} vs ${Math.round(data.student_average_bpm)} bpm`
            : "BPM estimate unavailable"}
        </span>
      </div>

      {chartData.length === 0 ? (
        <p className="text-sm text-ink-faint py-6">Not enough data to chart a tempo curve.</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
            {data.flagged_regions.map((region, i) => (
              <ReferenceArea
                key={i}
                x1={region.start}
                x2={region.end}
                fill={region.label === "dragging" ? "#A67C3D" : "#6E8F6B"}
                fillOpacity={0.08}
                strokeOpacity={0}
              />
            ))}
            <ReferenceLine y={1.0} stroke="#DDD5C7" />
            <XAxis dataKey="time" type="number" domain={["dataMin", "dataMax"]} tickFormatter={formatTime} stroke="#A69B8A" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#A69B8A" fontSize={11} domain={["auto", "auto"]} tickLine={false} axisLine={false} width={32} />
            <Tooltip
              contentStyle={{ background: "#FAF7F0", border: "1px solid #DDD5C7", borderRadius: 4, fontSize: 12, fontFamily: "IBM Plex Sans" }}
              labelFormatter={(t) => formatTime(Number(t))}
              formatter={(value: number) => [value.toFixed(2), "pace ratio"]}
            />
            <Line type="monotone" dataKey="ratio" stroke="#6E8F6B" dot={false} strokeWidth={1.75} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
