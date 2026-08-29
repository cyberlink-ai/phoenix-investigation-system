import { useEffect, useState } from "react";
import { getHealth } from "../api/client";

export default function StatusBadge() {
  const [status, setStatus] = useState("checking");
  const [dbConnected, setDbConnected] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then((data) => {
        if (cancelled) return;
        setStatus(data.status === "ok" ? "online" : "error");
        setDbConnected(data.database_connected);
      })
      .catch(() => {
        if (!cancelled) setStatus("offline");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const color =
    status === "online" ? "bg-console-accent" : status === "checking" ? "bg-console-warn" : "bg-console-alert";

  return (
    <div className="flex items-center gap-2 text-sm text-console-muted">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      <span>Backend: {status}</span>
      {dbConnected !== null && (
        <span className="ml-2 text-console-muted">
          · DB: {dbConnected ? "connected" : "not configured"}
        </span>
      )}
    </div>
  );
}
