# Design Blueprint: [Feature Name]

**Status:** Draft
**Owning Brief:** `docs/product/briefs/[feature_name].md`
**Data Contract:** `docs/product/contracts/[feature_name].md`

## 🗺️ State Flow (Mermaid)
[Insert Mermaid.js state diagram here mapping the user journey, including 3rd-party redirects]

## 🧩 Component Hierarchy (Atomic Breakdown)
- **Organism:** [e.g., Settings Layout]
  - **Molecule:** [e.g., Webhook Form]
    - **Atoms:** `shadcn/ui` [Input, Button, Label, Card]
    - **Icons:** `lucide-react` [e.g., AlertCircle, Check]

## 🎛️ UI State Mapping
| State | Trigger | Visual Behavior | Copy / Content Dictionary Key |
| :--- | :--- | :--- | :--- |
| **Empty** | No data exists | Show placeholder illustration and CTA | `content.feature.empty` |
| **Loading** | Awaiting API | Disable inputs, show spinner | `content.global.loading` |
| **Error** | API/Validation fail | Highlight invalid fields in red | `content.feature.error` |
| **Success** | API returns 200 | Show confirmation toast, redirect | `content.feature.success` |

## 🎨 Mobile-First Layout Tokens
- **Container:** `flex flex-col md:flex-row gap-4 p-4`
- **Responsive Behavior:** [e.g., Stack form elements vertically on mobile, side-by-side on desktop]

## 🔒 Security & Analytics Boundaries
- **Masked Data:** [List any fields that must visually hide PII/Secrets]
- **Telemetry Action:** [The exact UI button click that triggers the 'Hero Action' event]