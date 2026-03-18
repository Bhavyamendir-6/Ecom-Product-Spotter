"use client";

export default function HistoryError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="text-center py-12 space-y-4">
      <h2 className="text-xl font-semibold">Failed to load history</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
      >
        Try again
      </button>
    </div>
  );
}
