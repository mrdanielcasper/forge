# Design Handoff: Discord Integration

## Purpose
Define the Webhook Settings flow so Engineering can implement the first usable version without inventing behavior during build.

## Primary User
- Agency Operator Owen
- Secondary user: Service Business Manager Maya

## Core User Story
As a time-starved operator, I want to add a Discord webhook URL and know whether setup worked so I can trust that workflow alerts will reach the place my team already watches.

## Primary Action
- Save a Discord webhook URL.

## Screen Scope
- A single Webhook Settings panel or page.
- One primary form field for the webhook URL.
- A clear explanation of why this matters.
- A visible confirmation state after save.

## Information Hierarchy
1. Title and short value statement.
2. Webhook URL input.
3. Guidance text with an example or where to find the webhook URL.
4. Primary action button.
5. Current status or last saved state.

## Recommended Copy Direction
- Title: Connect Discord Alerts
- Supporting copy: Send workflow alerts to the Discord channel your team already uses.
- Input label: Discord webhook URL
- Primary button: Save webhook
- Success message: Discord webhook saved. Alerts will use this channel.
- Error message: That webhook URL does not look valid. Check the value and try again.

## Flow
1. User opens Webhook Settings.
2. User sees a short explanation and one visible primary action.
3. User pastes a webhook URL.
4. User submits.
5. System shows one of the defined states below.

## States
### Empty State
- Show a short explanation of what Discord alerts do.
- Show an empty input and a disabled or neutral status area.
- The primary action is available once the field has content.

### Validation Error State
- Trigger on malformed URL input.
- Keep the user input visible.
- Show inline guidance near the field.
- Do not clear the form.

### Loading State
- Disable the input and submit button while save is in progress.
- Show a lightweight saving indicator.
- Prevent duplicate submission.

### Success State
- Confirm that the webhook was saved.
- Display the masked webhook value or a configured status summary.
- Make it obvious the setup is complete without exposing the sensitive value.

### Server Error State
- Show a retry-oriented message.
- Keep the user's input if safe to do so.
- Distinguish this from validation failure.

## Accessibility Requirements
- The input needs a programmatically associated label.
- Validation and success messages need to be announced clearly.
- The submit path must work by keyboard only.
- Focus should move predictably after submit outcomes.

## Component Outline
- Settings panel container
- Field label and help text
- Webhook URL text input
- Inline validation message
- Primary action button
- Status summary or alert banner

## State Variables For Engineering
- webhookUrl
- validationError
- submissionStatus: idle | loading | success | error
- maskedWebhookUrl

## Analytics Expectations
- Fire `webhook_settings_opened` when the panel loads.
- Fire `webhook_validation_failed` on rejected malformed input.
- Fire `webhook_saved` on successful save.

## Implementation Notes
- Do not log the raw webhook URL.
- Preserve enough context in the UI for the user to understand what happened.
- Keep the first release intentionally narrow; avoid adding channel selection, test messages, or secondary configuration controls.