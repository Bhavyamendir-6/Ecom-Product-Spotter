"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check } from "lucide-react";
import { useState } from "react";

export function ReportViewer({ report }: { report: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <div className="flex justify-end mb-4">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 text-sm border border-border rounded-md hover:bg-muted"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" /> Copied
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" /> Copy Report
            </>
          )}
        </button>
      </div>
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
      </div>
    </div>
  );
}
