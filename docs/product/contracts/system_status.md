# Data Contract: System Status

## API: GET /api/v1/system/status

**Success Response Payload (200 OK):**
```json
{
  "status": "operational",
  "version": "1.0.0"
}
```

**Error Response Payload (500 / 503):**
```json
{
  "detail": "Internal Server Error"
}
```

## Failure & Retry Semantics
- **Network Failure / 5xx:** The frontend must intercept the error and display the explicit fallback UI defined in `content.ts` (`systemStatus.error`).
- **Retries:** The frontend will not automatically retry to prevent thundering herds during an outage. Retries are strictly manual via the "Refresh Status" user action.