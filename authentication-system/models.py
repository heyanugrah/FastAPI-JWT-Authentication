from sqlalchemy import Boolean, Column, Integer, String
from database import Base

#postgres
# class DBUser(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     role = Column(String, default="user")
#     disabled = Column(Boolean, default=False)


#mysql
class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Add a length of 50 for username and email
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    # Add a length of 255 for the hashed password
    hashed_password = Column(String(255))
    role = Column(String(50), default="user")
    disabled = Column(Boolean, default=False)