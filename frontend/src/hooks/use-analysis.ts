"use client";

import useSWR from "swr";
import { getAnalysis } from "@/lib/api";
import type { AnalysisResponse } from "@/lib/types";

export function useAnalysis(jobId: string) {
  const { data, error, isLoading, mutate } = useSWR<AnalysisResponse>(
    `/api/analysis/${jobId}`,
    () => getAnalysis(jobId),
    {
      refreshInterval: (data) => {
        if (
          data?.status === "completed" ||
          data?.status === "failed"
        ) {
          return 0;
        }
        return 2000;
      },
    }
  );

  return { analysis: data, error, isLoading, mutate };
}
