# Naming conventions

- A use case is a class with a single `execute()` method, named after a verb
  (`PrintInvoice`).
- DTOs mirror the domain objects: one file per entity (`dto/invoice/supplier.py`
  for `entities/supplier.py`) holding `<Entity>In` / `<Entity>Out`. A DTO that
  belongs to a use case only is named `<UseCase>In` / `<UseCase>Out`.
- ORM models are named `<Entity>Model` (e.g. `InternalRequestLogModel`).
- Repository implementations are named `Alchemy<Entity>Repository` and
  inherit from `BaseAlchemyRepository`.
- A domain entity never shares its name with an ORM model - mapping happens
  inside the repository.
- Repository methods follow a fixed contract: `get` always looks up by the
  entity's key, `delete` always takes that same key, and `save` always takes
  the domain entity itself (handles both insert and update).
- Any lookup that is not by that key gets a `_by_<field>` suffix (e.g.
  `get_by_name`), so a bare `get`/`delete` always means "by key".
- Entities never get their mutable fields set directly from outside -
  changes go through `create` (construction) and `update` (mutation), which
  enforce the entity's invariants. Shared validation lives in a private
  static/class `_validate` method called by both.
- Value objects are frozen dataclasses validated in `__post_init__`.
- `_validate` checks the values supplied by the caller of the service with
  the functions of `app/domain/shared/validation.py`
  (`validate_text(name=name, max_length=100)` - the keyword is the reported
  field); the first rejected value raises `DomainValidationError`.
- An entity never builds another entity or value object and does not check
  them. `create` gets them already built; putting them together is the job
  of the use case.
- Logic stays inline in use case `execute` methods and endpoint functions -
  no private helper methods there.
- Lines are wrapped at 80 characters.
