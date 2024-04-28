from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

PSQL_ADDRESS = "postgresql+psycopg://usama:0000@localhost/tritsk"

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
