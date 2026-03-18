import { SearchForm } from "@/components/search-form";
import { getHistory } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import { TrendingUp } from "lucide-react";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let recentAnalyses: Awaited<ReturnType<typeof getHistory>> = [];
  try {
    recentAnalyses = await getHistory(5, 0);
  } catch {
    // Backend may not be running yet
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="text-center space-y-6 max-w-2xl">
        <div className="flex items-center justify-center gap-3">
          <TrendingUp className="w-10 h-10 text-primary" />
          <h1 className="text-4xl font-bold">Product Spotter</h1>
        </div>

        <p className="text-lg text-muted-foreground">
          Discover trending product opportunities by analyzing Reddit
          discussions across 7 product-focused subreddits. Get scored
          opportunities and actionable seller reports.
        </p>

        <div className="flex justify-center">
          <SearchForm />
        </div>
      </div>

      {recentAnalyses.length > 0 && (
        <div className="mt-16 w-full max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">Recent Analyses</h2>
          <div className="space-y-2">
            {recentAnalyses.map((a) => (
              <Link
                key={a.job_id}
                href={`/analysis/${a.job_id}`}
                className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div>
                  <span className="font-medium">{a.keyword}</span>
                  <span className="ml-3 text-sm text-muted-foreground">
                    {formatDate(a.created_at)}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  {a.top_score != null && (
                    <span className="text-sm font-mono">
                      {a.top_score.toFixed(3)}
                    </span>
                  )}
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(a.status)}`}
                  >
                    {a.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-4 text-center">
            <Link
              href="/history"
              className="text-sm text-primary hover:underline"
            >
              View all analyses
            </Link>
          </div>
        </div>
      )}
    </main>
  );
}
