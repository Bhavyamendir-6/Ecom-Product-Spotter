import { getReport } from "@/lib/api";
import { ReportViewer } from "@/components/report-viewer";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

interface PageProps {
  params: Promise<{ jobId: string }>;
}

export default async function ReportPage({ params }: PageProps) {
  const { jobId } = await params;
  const report = await getReport(jobId);

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
            Report: &ldquo;{report.keyword}&rdquo;
          </h1>
        </div>
      </div>

      <div className="border border-border rounded-lg p-6">
        <ReportViewer report={report.report} />
      </div>
    </div>
  );
}
