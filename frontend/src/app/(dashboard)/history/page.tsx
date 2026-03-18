import { getHistory } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function HistoryPage() {
  let history: Awaited<ReturnType<typeof getHistory>> = [];
  try {
    history = await getHistory(50, 0);
  } catch {
    // Backend may not be running
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analysis History</h1>

      {history.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <p>No analyses yet. Start one from the home page.</p>
        </div>
      ) : (
        <div className="border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left p-3 font-medium">Keyword</th>
                <th className="text-left p-3 font-medium">Status</th>
                <th className="text-left p-3 font-medium">Started</th>
                <th className="text-left p-3 font-medium">Completed</th>
                <th className="text-right p-3 font-medium">Top Score</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.job_id} className="border-b hover:bg-muted/30">
                  <td className="p-3 font-medium">{h.keyword}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(h.status)}`}
                    >
                      {h.status}
                    </span>
                  </td>
                  <td className="p-3 text-muted-foreground">
                    {formatDate(h.created_at)}
                  </td>
                  <td className="p-3 text-muted-foreground">
                    {h.completed_at ? formatDate(h.completed_at) : "-"}
                  </td>
                  <td className="p-3 text-right font-mono">
                    {h.top_score != null ? h.top_score.toFixed(3) : "-"}
                  </td>
                  <td className="p-3">
                    <Link
                      href={`/analysis/${h.job_id}`}
                      className="text-primary hover:underline text-sm"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
