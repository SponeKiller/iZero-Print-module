# Errors and responses

Every response is a `ResponseContainer` (`message_id`, `message`, `data`).

- Use cases raise subclasses of `ApplicationError`.
- `app/infrastructure/api/errors/` maps each of them to a
  (`MessageId`, HTTP status) pair; `main.py` registers one handler for all.
- Endpoints let these errors propagate, so `get_db` rolls the transaction
  back before the response is built.
- An exception is caught only where the code knows how to handle it,
  never "to be safe".
- Every error from UseCase is always from applicationError (
  propagate domainError is not allowed)
- Anything else ends in the global fallback handler: Sentry +
  `SYSTEM_INTERNAL_FAIL` (500).

`MessageId` format: 2 digits main entity, 2 digits sub-entity, 3 digits
counter. `90xxxxx` (system) is shared across all iZero services and must
keep the same values as the auth service.
