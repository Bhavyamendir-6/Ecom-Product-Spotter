import { getRecommendationColor } from "@/lib/utils";

export function ScoreBadge({ recommendation }: { recommendation: string }) {
  const label = recommendation.split(" - ")[0] || recommendation;
  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${getRecommendationColor(recommendation)}`}
    >
      {label}
    </span>
  );
}
