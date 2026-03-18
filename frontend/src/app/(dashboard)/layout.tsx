import Link from "next/link";
import { TrendingUp, Home, Clock } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen">
      <nav className="border-b border-border px-6 py-3 flex items-center gap-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <TrendingUp className="w-5 h-5 text-primary" />
          Product Spotter
        </Link>
        <div className="flex items-center gap-4 ml-auto text-sm">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <Home className="w-4 h-4" /> Home
          </Link>
          <Link
            href="/history"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <Clock className="w-4 h-4" /> History
          </Link>
        </div>
      </nav>
      <main className="p-6 max-w-7xl mx-auto">{children}</main>
    </div>
  );
}
