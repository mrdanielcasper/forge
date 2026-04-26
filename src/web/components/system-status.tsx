import { useCallback, useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface StatusResponse {
  status: string;
  version: string;
}

export function SystemStatus() {
  const [data, setData] = useState<StatusResponse | null>(null);
  const [error, setError] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/system/status");
      if (!res.ok) throw new Error("Failed to fetch");
      const json = await res.json();
      setData(json);
      setError(false);
    } catch {
      setError(true);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return (
    <Card className="w-full max-w-md mx-auto mt-8 border-border">
      <CardHeader>
        <CardTitle className="text-xl font-bold text-foreground">System Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error ? (
          <p className="text-destructive font-medium">Failed to reach API.</p>
        ) : !data ? (
          <p className="text-muted-foreground">Loading status...</p>
        ) : (
          <div className="flex flex-col space-y-2">
            <p className="text-foreground">
              Status: <span className="font-semibold text-primary">{data.status}</span>
            </p>
            <p className="text-sm text-muted-foreground">Version: {data.version}</p>
          </div>
        )}
        <Button onClick={fetchStatus} variant="secondary" className="w-full">
          Refresh Status
        </Button>
      </CardContent>
    </Card>
  );
}
