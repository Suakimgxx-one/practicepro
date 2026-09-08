import { formatTime } from "@/lib/formatTime";

interface RegionsListProps {
  regions: { start: number; end: number; label?: string }[];
  emptyMessage: string;
}

const LABEL_TEXT: Record<string, string> = {
  dragging: "Dragging",
  rushing: "Rushing",
  louder_than_reference: "Louder than reference",
  quieter_than_reference: "Quieter than reference",
};

export function RegionsList({ regions, emptyMessage }: RegionsListProps) {
  if (regions.length === 0) {
    return <p className="text-sm text-ink-500 py-2">{emptyMessage}</p>;
  }
  return (
    <ul className="mt-2 divide-y divide-border-subtle">
      {regions.map((region, i) => (
        <li key={i} className="flex items-center justify-between py-2 text-sm">
          <span className="text-ink-300 tabular-nums">{formatTime(region.start)}–{formatTime(region.end)}</span>
          {region.label && <span className="text-ink-500">{LABEL_TEXT[region.label] ?? region.label}</span>}
        </li>
      ))}
    </ul>
  );
}
