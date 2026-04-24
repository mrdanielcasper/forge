import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// test.describe('Accessibility (WCAG) Audits', () => {
//   test('The Webhook Settings page should have zero a11y violations', async ({ page }) => {
//     // 1. Navigate to the page you are testing
//     await page.goto('/settings/webhooks');

//     // 2. Run the Axe-core scanner
//     const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

//     // 3. Assert that the violations array is completely empty
//     expect(accessibilityScanResults.violations).toEqual([]);
//   });
// });
