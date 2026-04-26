import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("Accessibility (WCAG) Audits", () => {
  test("The landing page scaffold should have zero a11y violations", async ({ page }) => {
    // 1. Intercept the API call so Vite doesn't try to proxy it to a dead backend
    await page.route("**/api/v1/system/status", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "operational", version: "1.0.0" }),
      });
    });

    // 2. Navigate to the page you are testing
    await page.goto("/");

    // 3. Wait for the React app to mount so we know the scaffold is working
    await page.waitForSelector("text=Solopreneur OS");

    // 4. Run the Axe-core scanner
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

    // 5. Assert that the violations array is completely empty
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
