from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django_mongodb_backend.fields import ArrayField

from accounts.passwords import is_legacy_bcrypt_hash, verify_legacy_bcrypt


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create(self, email: str, name: str, password: str | None, **extra: Any) -> User:
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email).lower().strip(), name=name.strip(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, name: str, password: str | None = None, **extra: Any) -> User:
        extra.setdefault("is_staff", False)
        return self._create(email, name, password, **extra)

    def create_superuser(self, email: str, name: str, password: str | None = None, **extra: Any) -> User:
        extra["is_staff"] = True
        return self._create(email, name, password, **extra)


class User(AbstractBaseUser):
    """An account. Stored in the existing ``users`` collection; field names are unchanged."""

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # JTIs of active refresh tokens (one per signed-in device).
    refresh_token_ids = ArrayField(
        models.CharField(max_length=64),
        default=list,
        blank=True,
        db_column="refreshTokens",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="createdAt")
    updated_at = models.DateTimeField(auto_now=True, db_column="updatedAt")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email

    def check_password(self, raw_password: str) -> bool:
        """
        Verify a password, transparently upgrading legacy bcrypt hashes.

        On a successful login against a legacy hash the password is re-hashed with the
        current Django hasher, so each account is migrated the first time it signs in.
        """
        if is_legacy_bcrypt_hash(self.password):
            if not verify_legacy_bcrypt(raw_password, self.password):
                return False
            self.set_password(raw_password)
            self.save(update_fields=["password", "updated_at"])
            return True
        return super().check_password(raw_password)
