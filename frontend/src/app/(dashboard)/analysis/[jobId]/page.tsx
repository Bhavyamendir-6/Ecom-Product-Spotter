import { getAnalysis } from "@/lib/api";
import { AnalysisProgress } from "@/components/analysis-progress";
import { formatDate } from "@/lib/utils";
import Link from "next/link";
import { BarChart3, FileText, TrendingUp } from "lucide-react";

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default async function AnalysisPage({ params }: PageProps) {
  const { jobId } = await params;
  let analysis;
  try {
    analysis = await getAnalysis(jobId);
  } catch {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold">Analysis not found</h2>
        <p className="text-muted-foreground mt-2">
          The analysis with ID {jobId} does not exist.
        </p>
      </div>
    );
  }

  const isInProgress =
    analysis.status !== "completed" && analysis.status !== "failed";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">
          Analysis: &ldquo;{analysis.keyword}&rdquo;
        </h1>
        <p className="text-muted-foreground mt-1">
          Started {formatDate(analysis.created_at)}
          {analysis.completed_at &&
            ` | Completed ${formatDate(analysis.completed_at)}`}
        </p>
      </div>

      {isInProgress ? (
        <div className="max-w-md">
          <h2 className="text-lg font-semibold mb-4">Pipeline Progress</h2>
          <AnalysisProgress jobId={jobId} />
        </div>
      ) : analysis.status === "failed" ? (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="font-semibold text-red-800">Analysis Failed</h2>
          <p className="mt-2 text-red-700">{analysis.error}</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-border rounded-lg">
              <div className="text-sm text-muted-foreground">Posts Found</div>
              <div className="text-2xl font-bold mt-1">
                {analysis.trending_terms?.length ?? 0}
              </div>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <div className="text-sm text-muted-foreground">Scored</div>
              <div className="text-2xl font-bold mt-1">
                {analysis.scored_terms?.length ?? 0}
              </div>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <div className="text-sm text-muted-foreground">Top Score</div>
              <div className="text-2xl font-bold mt-1">
                {analysis.scored_terms?.[0]?.opportunity_score.toFixed(3) ??
                  "N/A"}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Link
              href={`/analysis/${jobId}/trends`}
              className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted/50"
            >
              <TrendingUp className="w-4 h-4" /> View Trends
            </Link>
            <Link
              href={`/analysis/${jobId}/scores`}
              className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted/50"
            >
              <BarChart3 className="w-4 h-4" /> View Scores
            </Link>
            <Link
              href={`/analysis/${jobId}/report`}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90"
            >
              <FileText className="w-4 h-4" /> View Report
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
