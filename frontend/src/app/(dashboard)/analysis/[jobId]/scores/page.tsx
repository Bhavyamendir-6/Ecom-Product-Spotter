import { getScores, getAnalysis } from "@/lib/api";
import { ScoreTable } from "@/components/score-table";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default async function ScoresPage({ params }: PageProps) {
  const { jobId } = await params;
  const [analysis, scores] = await Promise.all([
    getAnalysis(jobId),
    getScores(jobId),
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
            Scored Opportunities: &ldquo;{analysis.keyword}&rdquo;
          </h1>
          <p className="text-muted-foreground">
            {scores.length} posts scored by e-commerce opportunity
          </p>
        </div>
      </div>

      <div className="border border-border rounded-lg overflow-hidden">
        <ScoreTable scores={scores} />
      </div>
    </div>
  );
}
