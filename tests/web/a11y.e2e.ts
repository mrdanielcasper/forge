import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("Accessibility (WCAG) Audits", () => {
  test("The landing page scaffold should have zero a11y violations", async ({ page }) => {
    // 1. Navigate to the page you are testing
    await page.goto("/");

    // 2. Wait for the React app to mount so we know the scaffold is working
    await page.waitForSelector("text=Solopreneur OS");

    // 3. Run the Axe-core scanner
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

    // 4. Assert that the violations array is completely empty
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
