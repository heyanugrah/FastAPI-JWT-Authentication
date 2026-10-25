from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#postgres
# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/yourdb"

#mysql
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root%40123@localhost:3306/yourdb"
# Python safely encodes "root@123" into "root%40123"
password = quote_plus("root@123")
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:{password}@localhost:3306/yourdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to create a new database session for every request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
