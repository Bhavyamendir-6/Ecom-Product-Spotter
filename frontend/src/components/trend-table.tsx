import type { TrendTerm } from "@/lib/types";
import { ExternalLink } from "lucide-react";
import { ColumnTooltip } from "./column-tooltip";

export function TrendTable({ trends }: { trends: TrendTerm[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left p-3 font-medium">Title</th>
            <th className="text-right p-3 font-medium">
              <ColumnTooltip
                label="Score"
                definition="Raw Reddit upvote count for this post at time of fetching."
                calculation="Direct value from Reddit API (post.score)"
                align="right"
              />
            </th>
            <th className="text-right p-3 font-medium">
              <ColumnTooltip
                label="Comments"
                definition="Total number of comments on the post at time of fetching."
                calculation="Direct value from Reddit API (post.num_comments)"
                align="right"
              />
            </th>
            <th className="text-right p-3 font-medium">
              <ColumnTooltip
                label="Velocity"
                definition="Rate of new comments per hour — a proxy for how actively the discussion is growing right now."
                calculation="num_comments / hours_since_posted&#10;(post age derived from created_utc)"
                align="right"
              />
            </th>
            <th className="text-right p-3 font-medium">
              <ColumnTooltip
                label="Upvote %"
                definition="Percentage of votes that are upvotes — indicates overall community approval."
                calculation="upvote_ratio × 100&#10;(Reddit API field, e.g. 0.97 → 97%)"
                align="right"
              />
            </th>
            <th className="text-left p-3 font-medium">
              <ColumnTooltip
                label="Subreddit"
                definition="The Reddit community where this post was found. Different subreddits attract different buyer personas."
                align="left"
              />
            </th>
            <th className="text-left p-3 font-medium">
              <ColumnTooltip
                label="Source"
                definition="How this post was discovered: via keyword search or from the subreddit's hot feed filtered by keyword relevance."
                calculation="reddit_search — matched your keyword&#10;reddit_hot — top post in hot feed"
                align="left"
              />
            </th>
            <th className="p-3"></th>
          </tr>
        </thead>
        <tbody>
          {trends.map((t, i) => (
            <tr key={i} className="border-b hover:bg-muted/30">
              <td className="p-3 max-w-xs truncate" title={t.title}>
                {t.title}
              </td>
              <td className="p-3 text-right font-mono">{t.score}</td>
              <td className="p-3 text-right font-mono">{t.num_comments}</td>
              <td className="p-3 text-right font-mono">
                {t.comment_velocity.toFixed(1)}
              </td>
              <td className="p-3 text-right font-mono">
                {(t.upvote_ratio * 100).toFixed(0)}%
              </td>
              <td className="p-3 text-muted-foreground">r/{t.subreddit}</td>
              <td className="p-3 text-muted-foreground">{t.source}</td>
              <td className="p-3">
                <a
                  href={t.post_url}
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
