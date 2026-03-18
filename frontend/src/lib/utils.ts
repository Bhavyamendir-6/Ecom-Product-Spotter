import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getRecommendationColor(recommendation: string): string {
  if (recommendation.startsWith("High")) return "bg-green-100 text-green-800";
  if (recommendation.startsWith("Moderate"))
    return "bg-yellow-100 text-yellow-800";
  if (recommendation.startsWith("Low")) return "bg-orange-100 text-orange-800";
  return "bg-red-100 text-red-800";
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800";
    case "failed":
      return "bg-red-100 text-red-800";
    case "pending":
      return "bg-gray-100 text-gray-800";
    default:
      return "bg-blue-100 text-blue-800";
  }
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
