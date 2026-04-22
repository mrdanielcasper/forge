# Feature Contract: Discord Webhook

**Status:** Draft
**Version:** 0.1.0
**Owning Brief:** docs/product/briefs/discord_integration.md

## User Problem
The user needs a fast, low-risk way to configure Discord alerts without guessing whether setup worked.

## Functional Summary
- Trigger: User saves a Discord webhook URL from the webhook settings panel.
- Success outcome: The system stores or simulates storage of the webhook configuration and confirms the saved state.

## Business Rules
- The webhook URL is required.
- The input must look like a Discord webhook URL before submission.
- The stored or returned value must be masked in any non-form output.

## Request Interface
### POST /api/webhooks

```json
{
  "provider": "discord",
  "webhook_url": "https://discord.com/api/webhooks/..."
}
```

## Success Response
### 201 Created

```json
{
  "id": "wh_123",
  "provider": "discord",
  "masked_webhook_url": "https://discord.com/api/webhooks/***",
  "status": "configured"
}
```

## Error Responses
- 400 Bad Request: malformed webhook URL.
- 409 Conflict: a duplicate configuration already exists.
- 500 Server Error: unexpected failure while saving configuration.

## UI States
- Loading: Disable submit and show in-progress feedback.
- Success: Confirm configuration and display masked value.
- Empty: Explain why the webhook is useful and what input is required.
- Error: Show actionable validation or retry messaging.

## Permissions And Security
- Only authenticated users can configure a webhook.
- Never log the raw webhook URL.
- Mask sensitive values in UI summaries, telemetry, and support artifacts.

## Analytics Events
- webhook_settings_opened
- webhook_validation_failed
- webhook_saved

## Operational Risks
- Setup friction may prevent activation.
- Logging mistakes could leak sensitive integration data.

## Rollout Notes
Use a mocked endpoint first. Promote to a live Discord call only after setup completion and demand are validated.