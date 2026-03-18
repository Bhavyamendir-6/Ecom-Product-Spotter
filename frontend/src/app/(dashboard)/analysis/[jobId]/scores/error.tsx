"use client";

export default function ScoresError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="text-center py-12 space-y-4">
      <h2 className="text-xl font-semibold">Scores not available yet</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
      >
        Retry
      </button>
    </div>
  );
}
