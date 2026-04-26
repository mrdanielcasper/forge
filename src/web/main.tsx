import { SystemStatus } from "@/components/system-status";
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <main className="flex min-h-screen flex-col items-center justify-center bg-background text-foreground p-4 gap-8">
      <div className="text-center space-y-4 max-w-md">
        <h1 className="text-3xl font-bold tracking-tight">Solopreneur OS</h1>
        {/* FIX: Changed from <p> to <h2> to fix WCAG heading order violation */}
        <h2 className="text-lg text-muted-foreground">
          Factory floor initialized. Golden Exemplar booted and ready for blueprints.
        </h2>
      </div>

      <SystemStatus />
    </main>
  </React.StrictMode>,
);
