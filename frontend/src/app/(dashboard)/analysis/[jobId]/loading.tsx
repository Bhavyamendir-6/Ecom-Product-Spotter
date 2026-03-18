export default function AnalysisLoading() {
  return (
    <div className="space-y-8 animate-pulse">
      <div>
        <div className="h-8 bg-muted rounded w-64" />
        <div className="h-4 bg-muted rounded w-48 mt-2" />
      </div>
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-muted rounded-lg" />
        ))}
      </div>
    </div>
  );
}
