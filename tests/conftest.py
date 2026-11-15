import os

# Settings are read when `app.infrastructure.config` is imported, so the
# required variables must exist before any test imports the application.
# No test connects to the database.
os.environ.setdefault("DATABASE_HOSTNAME", "localhost")
os.environ.setdefault("DATABASE_PORT", "5432")
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "")
os.environ.setdefault("CORS_ALLOW_METHODS", "")
os.environ.setdefault("CORS_ALLOW_HEADERS", "")
os.environ["SENTRY_DSN"] = ""
