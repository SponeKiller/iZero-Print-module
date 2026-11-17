# Observability

- Inbound calls: `HttpAuditMiddleware` -> `internal_request_log`,
  `internal_response_log`.
- Outbound calls: any `requests` call once `app.infrastructure.providers`
  is imported -> `external_request_log`, `external_response_log`.
- Sensitive headers and body fields are redacted (configurable in `.env`),
  unknown content types are never stored raw.
- Auditing never breaks the real call - DB errors in the audit are swallowed.
- Unhandled exceptions go to Sentry (`SENTRY_DSN`; empty disables it).
