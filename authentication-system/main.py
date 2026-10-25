# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# import jwt
#
# from schemas import User, Token
# from security import verify_password, create_access_token, SECRET_KEY, ALGORITHM
# from database import fake_users_db, get_user
#
# app = FastAPI(title="Modular FastAPI Auth")
#
# # Tells FastAPI where the login endpoint is located
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# # The security dependency that protects your routes
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # Decode the token to get the username
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except jwt.InvalidTokenError:
#         raise credentials_exception
#
#     # Verify the user still exists in the database
#     user = get_user(fake_users_db, username=username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# @app.get("/users/me", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
#
#
# # @app.post("/token", response_model=Token)
# # async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
# #     user = get_user(fake_users_db, form_data.username)
# #
# #     if not user or not verify_password(form_data.password, user.hashed_password):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect username or password",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )
# #
# #     access_token = create_access_token(data={"sub": user.username})
# #     return {"access_token": access_token, "token_type": "bearer"}
#
#
# #api key is required to access it
# @app.get("/secret-message")
# async def get_secret_message(current_user: User = Depends(get_current_user)):
#     """
#     A simple test endpoint to verify authentication is working.
#     """
#     return {
#         "message": f"Hello {current_user.username}! Authentication is working perfectly.",
#         "secret_code": 42
#     }
#
#
# #public api no authentication
# @app.get("/public")
# async def get_secret_message():
#     """
#     A simple test endpoint to verify authentication is working.
#     """
#     return {
#         "message": f"Hello World -Public API",
#         "secret_code": 42
#     }
#
#
# # Role checking {user /admin}
# class RoleChecker:
#     def __init__(self, allowed_roles: list):
#         self.allowed_roles = allowed_roles
#
#     def __call__(self, user: User = Depends(get_current_user)):
#         if user.role not in self.allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You do not have permission to perform this action"
#             )
#         return user
#
#
# # 1. Define your permission levels
# require_admin = RoleChecker(["admin"])
# require_user = RoleChecker(["user"])
# require_user_or_admin = RoleChecker(["admin", "user"])
#
#
# # 2. Apply to endpoints using dependencies
# @app.get("/admin/dashboard", dependencies=[Depends(require_admin)])
# async def admin_only_route():
#     """Only users with 'admin' role can access this."""
#     return {"message": "Welcome to the Admin Dashboard!"}
#
# @app.get("/user/dashboard", dependencies=[Depends(require_user)])
# async def admin_only_route():
#     """Only users with 'admin' role can access this."""
#     return {"message": "Welcome to the User Dashboard!"}
#
#
# @app.get("/common/dashboard", dependencies=[Depends(require_user_or_admin)])
# async def admin_only_route():
#     """Only users with 'admin or user' role can access this."""
#     return {"message": "Welcome to the Common Dashboard!"}
#
#
# @app.get("/user/profile")
# async def any_logged_in_user(current_user: User = Depends(get_current_user)):
#     """Any authenticated user can access this (John or Jane)."""
#     return {"message": f"Hello {current_user.username}, your role is {current_user.role}"}
#

#---------------------DATABASE------------------------------------------
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

import models
import schemas
from security import verify_password, create_access_token, get_password_hash, SECRET_KEY, ALGORITHM
from database import engine, get_db

# Automatically creates the tables in PostgreSQL if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PostgreSQL Auth API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Dependencies ---
# 1. The Bouncer (now queries PostgreSQL)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Fetch user from PostgreSQL
    user = db.query(models.DBUser).filter(models.DBUser.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# 2. Role Checker
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission"
            )
        return user


require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["user"])


# --- Routes ---

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user directly into PostgreSQL."""
    db_user = db.query(models.DBUser).filter(models.DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.DBUser(
        username=user.username,
        email=user.email,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Verify credentials against PostgreSQL
    user = db.query(models.DBUser).filter(models.DBUser.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/dashboard")
async def admin_dashboard(current_user: models.DBUser = Depends(require_admin)):
    return {"message": f"Welcome Admin {current_user.username}!"}


@app.get("/user/dashboard")
async def admin_dashboard(current_user: models.DBUser = Depends(require_user)):
    return {"message": f"Welcome User {current_user.username}!"}