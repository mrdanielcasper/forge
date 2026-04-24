import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground p-4">
      <div className="text-center space-y-4 max-w-md">
        <h1 className="text-3xl font-bold tracking-tight">Solopreneur OS</h1>
        <p className="text-muted-foreground">
          Frontend scaffold successfully booted. Ready for the Design and Engineering agents.
        </p>
      </div>
    </main>
  </React.StrictMode>,
);
