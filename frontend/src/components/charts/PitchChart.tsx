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

interface PitchChartProps {
  data: PitchResultData;
}

export function PitchChart({ data }: PitchChartProps) {
  const chartData = data.points.map((p) => ({ time: p.reference_time, cents: p.cents_deviation }));

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-medium text-ink-soft">Pitch</h3>
        <span className="text-xs text-ink-faint">
          {data.mean_absolute_cents_deviation.toFixed(1)} cents average deviation
        </span>
      </div>

      {chartData.length === 0 ? (
        <p className="text-sm text-ink-faint py-6">No voiced pitch data was found to compare.</p>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chartData} margin={{ top: 5, right: 4, left: -20, bottom: 0 }}>
            {data.flagged_regions.map((region, i) => (
              <ReferenceArea key={i} x1={region.start} x2={region.end} fill="#A6503D" fillOpacity={0.08} strokeOpacity={0} />
            ))}
            <ReferenceLine y={0} stroke="#DDD5C7" />
            <XAxis dataKey="time" type="number" domain={["dataMin", "dataMax"]} tickFormatter={formatTime} stroke="#A69B8A" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#A69B8A" fontSize={11} tickLine={false} axisLine={false} width={36} />
            <Tooltip
              contentStyle={{ background: "#FAF7F0", border: "1px solid #DDD5C7", borderRadius: 4, fontSize: 12, fontFamily: "IBM Plex Sans" }}
              labelFormatter={(t) => formatTime(Number(t))}
              formatter={(value: number) => [`${value.toFixed(1)} cents`, "deviation"]}
            />
            <Line type="monotone" dataKey="cents" stroke="#A67C3D" dot={false} strokeWidth={1.75} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
