"use client";

import { useEffect, useRef, useState } from "react";
import type { WsMessage } from "@/lib/types";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWsProgress(jobId: string) {
  const [message, setMessage] = useState<WsMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/analysis/${jobId}`);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event) => {
      const data: WsMessage = JSON.parse(event.data);
      setMessage(data);
      if (data.stage === "completed" || data.stage === "failed") {
        ws.close();
      }
    };

    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return () => {
      ws.close();
    };
  }, [jobId]);

  return { message, isConnected };
}
