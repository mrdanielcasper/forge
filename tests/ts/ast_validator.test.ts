import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, test } from "vitest";

describe("AST Validator (Layer 1 Eval)", () => {
  const testDir = path.join(__dirname, "temp_ast_test");

  beforeAll(() => {
    fs.mkdirSync(testDir, { recursive: true });
  });

  afterAll(() => {
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  test("Fails when inline styles are used", () => {
    const badCode =
      'export default function Bad() { return <div style={{ color: "red" }}>Fail</div>; }';
    const filepath = path.join(testDir, "BadStyle.tsx");
    fs.writeFileSync(filepath, badCode);

    expect(() => execSync(`node scripts/ast_validator.mjs ${filepath}`)).toThrow();
  });

  test("Passes with clean Tailwind and accessible images", () => {
    const goodCode =
      'export default function Good() { return <img src="/logo.png" alt="Logo" className="w-10" />; }';
    const filepath = path.join(testDir, "GoodComponent.tsx");
    fs.writeFileSync(filepath, goodCode);

    expect(() => execSync(`node scripts/ast_validator.mjs ${filepath}`)).not.toThrow();
  });
});
