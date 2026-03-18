"use client";

import { useWsProgress } from "@/hooks/use-ws-progress";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2, CheckCircle, XCircle } from "lucide-react";

const STAGES = [
  { key: "fetching", label: "Fetching Reddit trends", threshold: 20 },
  { key: "scoring", label: "Scoring opportunities", threshold: 50 },
  { key: "generating", label: "Generating report", threshold: 75 },
  { key: "completed", label: "Analysis complete", threshold: 100 },
];

export function AnalysisProgress({ jobId }: { jobId: string }) {
  const { message } = useWsProgress(jobId);
  const router = useRouter();

  useEffect(() => {
    if (message?.stage === "completed") {
      const timer = setTimeout(() => router.refresh(), 1500);
      return () => clearTimeout(timer);
    }
  }, [message, router]);

  const currentStage = message?.stage || "pending";
  const progress = message?.progress || 0;

  if (currentStage === "failed") {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center gap-2 text-red-800">
          <XCircle className="w-5 h-5" />
          <span className="font-medium">Analysis failed</span>
        </div>
        {message?.error && (
          <p className="mt-2 text-sm text-red-700">{message.error}</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="w-full bg-muted rounded-full h-3">
        <div
          className="bg-primary h-3 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="space-y-3">
        {STAGES.map((stage) => {
          const isActive = currentStage === stage.key;
          const isDone = progress > stage.threshold;

          return (
            <div key={stage.key} className="flex items-center gap-3">
              {isDone ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : isActive ? (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              ) : (
                <div className="w-5 h-5 rounded-full border-2 border-muted-foreground/30" />
              )}
              <span
                className={
                  isActive
                    ? "font-medium text-foreground"
                    : isDone
                    ? "text-muted-foreground"
                    : "text-muted-foreground/50"
                }
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
