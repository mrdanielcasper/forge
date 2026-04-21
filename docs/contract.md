# API Contract: [Feature Name]
**Status:** [Draft / Approved / Implemented]
**Version:** 1.0.0

## 1. Functional Summary
* **User Goal:** [e.g., "User wants to see their monthly spending breakdown."]
* **Trigger:** [e.g., "User clicks on the 'Insights' tab."]

## 2. Data Schema (The "Interface")
This defines exactly what the frontend expects to receive.

| Field | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Unique identifier | `550e8400-e29b...` |
| `amount` | Float | Transaction value | `42.50` |
| `category` | Enum | [Food, Rent, Fun, Tech] | `"Food"` |
| `timestamp` | ISO8601 | Date of entry | `"2026-04-20T...` |

## 3. Endpoints & Methods
Even if these are mocked, define them as if they were real.

### `GET /api/v1/insights`
* **Auth Required:** Yes (JWT)
* **Success Response (200):**
    ```json
    {
      "total_spend": 1250.00,
      "items": [...]
    }
    ```
* **Error States:**
    * `401`: Unauthorized (Redirect to Login)
    * `500`: Server Error (Show "Try again later" Toast)

## 4. UI State Requirements
* **Loading State:** Show `SkeletonLoader` for the chart.
* **Empty State:** Show "No data for this month" illustration.
* **Refresh Strategy:** Re-validate on window focus.