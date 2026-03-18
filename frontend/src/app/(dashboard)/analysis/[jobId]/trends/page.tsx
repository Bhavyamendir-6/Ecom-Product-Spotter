import { getTrends, getAnalysis } from "@/lib/api";
import { TrendTable } from "@/components/trend-table";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default async function TrendsPage({ params }: PageProps) {
  const { jobId } = await params;
  const [analysis, trends] = await Promise.all([
    getAnalysis(jobId),
    getTrends(jobId),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={`/analysis/${jobId}`}
          className="text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">
            Trending Posts: &ldquo;{analysis.keyword}&rdquo;
          </h1>
          <p className="text-muted-foreground">
            {trends.length} posts found across Reddit
          </p>
        </div>
      </div>

      <div className="border border-border rounded-lg overflow-hidden">
        <TrendTable trends={trends} />
      </div>
    </div>
  );
}
