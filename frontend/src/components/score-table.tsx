"use client";

import { useState } from "react";
import type { ScoredTerm } from "@/lib/types";
import { ScoreBadge } from "./score-badge";
import { ColumnTooltip } from "./column-tooltip";
import { ArrowUpDown, ExternalLink } from "lucide-react";

type SortKey = "opportunity_score" | "popularity_score" | "engagement_score" | "sentiment_signal" | "commercial_intent";

const SCORE_COLUMN_META: Record<SortKey, { definition: string; calculation: string }> = {
  opportunity_score: {
    definition: "Composite score (0–1) representing overall e-commerce potential of this Reddit post.",
    calculation:
      "0.30 × popularity\n+ 0.25 × engagement\n+ 0.20 × sentiment\n+ 0.25 × commercial intent",
  },
  popularity_score: {
    definition: "How popular this post is relative to all posts analyzed, based on upvote count.",
    calculation: "Normalized upvotes:\n(upvotes − min) / (max − min)",
  },
  engagement_score: {
    definition: "How actively people are commenting, measured as comment velocity over time.",
    calculation: "Normalized comment velocity:\ncomments / hours_since_posted",
  },
  sentiment_signal: {
    definition: "Community approval level — the ratio of upvotes to total votes cast.",
    calculation: "Reddit upvote_ratio field\n(e.g. 0.97 = 97% upvoted)",
  },
  commercial_intent: {
    definition: "Likelihood that this post represents a buying intent or product interest signal.",
    calculation:
      "Keyword matching score:\nmatches against product, brand,\nbuy, review, recommend, etc.",
  },
};

export function ScoreTable({ scores }: { scores: ScoredTerm[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("opportunity_score");
  const [sortAsc, setSortAsc] = useState(false);

  const sorted = [...scores].sort((a, b) => {
    const diff = a[sortKey] - b[sortKey];
    return sortAsc ? diff : -diff;
  });

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  };

  const SortHeader = ({ label, field }: { label: string; field: SortKey }) => (
    <th
      className="p-3 font-medium cursor-pointer hover:bg-muted/70"
      onClick={() => toggleSort(field)}
    >
      <div className="flex items-center gap-1 justify-end">
        <ColumnTooltip
          label={label}
          definition={SCORE_COLUMN_META[field].definition}
          calculation={SCORE_COLUMN_META[field].calculation}
          align="right"
        />
        <ArrowUpDown className="w-3 h-3 shrink-0" />
      </div>
    </th>
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left p-3 font-medium">Title</th>
            <SortHeader label="Score" field="opportunity_score" />
            <SortHeader label="Popularity" field="popularity_score" />
            <SortHeader label="Engagement" field="engagement_score" />
            <SortHeader label="Sentiment" field="sentiment_signal" />
            <SortHeader label="Commercial" field="commercial_intent" />
            <th className="text-left p-3 font-medium">
              <ColumnTooltip
                label="Recommendation"
                definition="Action tier based on the opportunity score."
                calculation={"≥ 0.75 → High\n≥ 0.50 → Moderate\n≥ 0.25 → Low\n< 0.25 → Minimal"}
                align="left"
              />
            </th>
            <th className="text-left p-3 font-medium">Subreddit</th>
            <th className="p-3"></th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((s, i) => (
            <tr key={i} className="border-b hover:bg-muted/30">
              <td className="p-3 max-w-xs truncate" title={s.title}>
                {s.title}
              </td>
              <td className="p-3 text-right font-mono font-bold">
                {s.opportunity_score.toFixed(3)}
              </td>
              <td className="p-3 text-right font-mono">
                {s.popularity_score.toFixed(3)}
              </td>
              <td className="p-3 text-right font-mono">
                {s.engagement_score.toFixed(3)}
              </td>
              <td className="p-3 text-right font-mono">
                {s.sentiment_signal.toFixed(3)}
              </td>
              <td className="p-3 text-right font-mono">
                {s.commercial_intent.toFixed(3)}
              </td>
              <td className="p-3">
                <ScoreBadge recommendation={s.recommendation} />
              </td>
              <td className="p-3 text-muted-foreground">r/{s.subreddit}</td>
              <td className="p-3">
                <a
                  href={s.post_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
