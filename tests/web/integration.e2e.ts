import { expect, test } from "@playwright/test";

test.describe("Full-Stack Integration", () => {
  test("The browser successfully fetches and renders live data from the FastAPI backend", async ({
    page,
  }) => {
    // 1. Navigate to the page (Notice we are NOT mocking the API route here)
    await page.goto("/");

    // 2. Wait for the React app to mount
    await page.waitForSelector("text=Solopreneur OS");

    // 3. Verify the frontend successfully parsed the LIVE API response
    // The live backend sends status="operational" and version="1.0.0"
    await expect(page.locator("text=operational")).toBeVisible();
    await expect(page.locator("text=Version: 1.0.0")).toBeVisible();
  });
});
