"use server";

import { redirect } from "next/navigation";

export async function createAnalysisAction(formData: FormData) {
  const keyword = formData.get("keyword") as string;
  if (!keyword?.trim()) return;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${apiUrl}/api/analysis/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword: keyword.trim() }),
  });

  if (!res.ok) {
    throw new Error("Failed to start analysis");
  }

  const data = await res.json();
  redirect(`/analysis/${data.job_id}`);
}
