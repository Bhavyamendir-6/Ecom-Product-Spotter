"use client";

import { useState } from "react";
import { Info } from "lucide-react";

interface ColumnTooltipProps {
  label: string;
  definition: string;
  calculation?: string;
  align?: "left" | "right";
}

export function ColumnTooltip({
  label,
  definition,
  calculation,
  align = "right",
}: ColumnTooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div
      className="relative inline-flex items-center gap-1 group"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      <span>{label}</span>
      <Info className="w-3 h-3 text-muted-foreground/60 group-hover:text-muted-foreground" />

      {visible && (
        <div
          className={`
            absolute z-50 top-full mt-1.5 w-64 rounded-lg
            bg-black text-white shadow-lg p-3 text-xs leading-relaxed
            ${align === "right" ? "right-0" : "left-0"}
          `}
        >
          <p className="font-semibold mb-1">{label}</p>
          <p className="text-gray-300">{definition}</p>
          {calculation && (
            <>
              <div className="border-t border-gray-600 my-2" />
              <p className="font-medium mb-0.5">How it&apos;s calculated</p>
              <p className="text-gray-300 font-mono text-[11px] whitespace-pre-wrap">
                {calculation}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
