"use client";

import { useFormStatus } from "react-dom";
import { createAnalysisAction } from "@/actions/analysis";
import { Search } from "lucide-react";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
    >
      <Search className="w-4 h-4" />
      {pending ? "Analyzing..." : "Analyze Trends"}
    </button>
  );
}

export function SearchForm() {
  return (
    <form action={createAnalysisAction} className="flex gap-3 w-full max-w-xl">
      <input
        name="keyword"
        type="text"
        required
        placeholder="e.g. wireless earbuds, mechanical keyboard, skincare..."
        className="flex-1 px-4 py-3 border border-border rounded-lg bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
      />
      <SubmitButton />
    </form>
  );
}
