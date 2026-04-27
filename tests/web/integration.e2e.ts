import { expect, test } from "@playwright/test";

test.describe("Full-Stack Integration", () => {
  test("The browser successfully fetches and renders live data from the FastAPI backend", async ({
    page,
  }) => {
    // 1. Navigate to the page (Hitting the LIVE unmocked API)
    await page.goto("/");

    // 2. Wait for the React app to mount
    await page.waitForSelector("text=Solopreneur OS");

    // 3. Verify the frontend successfully parsed the LIVE API response
    await expect(page.locator("text=operational")).toBeVisible();
    await expect(page.locator("text=Version: 1.0.0")).toBeVisible();
  });

  test("The browser handles and renders backend 500 errors correctly", async ({ page }) => {
    // 1. Intercept the live API call and forcefully return a 500 Error
    await page.route("**/api/v1/system/status", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal Server Error" }),
      });
    });

    // 2. Navigate to the page
    await page.goto("/");
    await page.waitForSelector("text=Solopreneur OS");

    // 3. Verify the fallback Error UI is displayed from content.ts
    await expect(page.locator("text=Failed to reach API.")).toBeVisible();
  });
});
