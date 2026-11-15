"""
Entrypoint for seeding default configuration data, run right after
`alembic upgrade head` (see entrypoint.sh). Every seed use case must be
idempotent.
"""
from sqlalchemy import func, select

from app.infrastructure.database.session import db_session

# Arbitrary fixed key for the advisory lock guarding this seed script.
SEED_LOCK_KEY = 514_907_263


def run() -> None:
    with db_session() as db:
        # Serialize concurrent replicas: without this, two replicas can both
        # observe a missing fixed-ID row and race on insert, crashing one of
        # them. Transaction-scoped lock auto-releases on commit/rollback
        # (db_session's exit).
        db.execute(select(func.pg_advisory_xact_lock(SEED_LOCK_KEY)))

        # Register seed use cases here, e.g.:
        # SeedDefaultSomething(AlchemySomethingRepository(db)).execute()


if __name__ == "__main__":
    run()
