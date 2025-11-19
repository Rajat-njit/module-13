# app/database_init.py
from app.database import engine, Base
from app.models import user, calculation  # noqa: F401 (imported for side-effects)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all tables."""
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    init_db()  # pragma: no cover
