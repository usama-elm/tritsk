from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from api.config import DB_ADRESS, DB_NAME, DB_PASSWORD, DB_USER

PSQL_ADDRESS = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_ADRESS}/{DB_NAME}"

engine = create_engine(PSQL_ADDRESS, echo=True, client_encoding="utf8")
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
    finally:
        db.close()
