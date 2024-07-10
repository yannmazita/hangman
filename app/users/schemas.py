from pydantic import BaseModel, validate_call

from app.auth.config import OAUTH_SCOPES
from app.schemas import Base, UuidMixin


class User(Base, UuidMixin):
    username: str
    hashed_password: str
    roles: str = ""


class UserBase(Base):
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(Base):
    username: str | None = None
    old_password: str | None = None
    new_password: str | None = None
    confirm_password: str | None = None
    roles: str | None = None

    @validate_call
    def __init__(self, **data):
        super().__init__(**data)
        self.validate_username()
        self.validate_passwords
        self.validate_roles

    def validate_username(self):
        if self.username is not None:
            if len(self.username) < 3:
                raise ValueError("Username must be at least 3 characters")
            if len(self.username) > 50:
                raise ValueError("Username must be at most 50 characters")

    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if self.old_password == self.new_password:
            raise ValueError("New password is the same as the old password")

    def validate_roles(self):
        if self.roles is not None:
            valid_roles = set(OAUTH_SCOPES.keys())
            given_roles = set(self.roles.split())
            if not given_roles.issubset(valid_roles):
                raise ValueError(f"Invalid roles: {given_roles - valid_roles}")


class UserRead(UserBase, UuidMixin):
    roles: str


class Users(BaseModel):
    users: list[UserRead]
    total: int
