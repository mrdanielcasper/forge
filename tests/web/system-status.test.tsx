import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
// 1. Explicitly add .tsx so ESM knows exactly what file to load
import { SystemStatus } from "../../src/web/components/system-status.tsx";

describe("SystemStatus Component", () => {
  it("renders the loading state initially", () => {
    render(<SystemStatus />);
    expect(screen.getByText("System Status")).toBeDefined();
    expect(screen.getByText("Loading status...")).toBeDefined();
  });
});
