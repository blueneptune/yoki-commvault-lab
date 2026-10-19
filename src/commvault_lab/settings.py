"""How the lab reaches a CommServe: config/<commcell>.env.

The same keys, and the same file format, as blt's own CommCell files, so
a file can be copied between the two. What is different is that the lab
has a token of its own: renewing an access token replaces the pair on
the CommServe, so two tools renewing one pair from two copies of the
file lock each other out. --config-dir or CV_LAB_CONFIG_DIR choose
another directory of the lab's own files.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LabSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    cv_base_url: str
    # "software": a CommServe you run. "saas": Commvault Cloud.
    cv_deployment: Literal["software", "saas"] = "software"
    cv_max_calls_per_hour: int | None = None
    # Either an access token, or a username and password. If both are
    # set the access token is used. With a refresh token the lab renews
    # the access token itself and rewrites these four lines (tokens.py).
    cv_access_token: SecretStr | None = None
    cv_refresh_token: SecretStr | None = None
    cv_token_expires_at: datetime | None = None
    cv_token_renewable_until: datetime | None = None
    cv_username: str | None = None
    cv_password: SecretStr | None = None
    cv_verify_tls: bool = True
    cv_ca_bundle: Path | None = None
    cv_page_size: int = 500
    cv_timeout_seconds: float = 120.0

    @field_validator(
        "cv_access_token",
        "cv_refresh_token",
        "cv_token_expires_at",
        "cv_token_renewable_until",
        "cv_username",
        "cv_password",
        "cv_max_calls_per_hour",
        mode="before",
    )
    @classmethod
    def _blank_is_unset(cls, value: object) -> object:
        # "CV_USERNAME=" left empty in the file means "not using this".
        return None if isinstance(value, str) and not value.strip() else value

    @model_validator(mode="after")
    def _has_credentials(self) -> LabSettings:
        if not self.cv_access_token and not (self.cv_username and self.cv_password):
            raise ValueError("set CV_ACCESS_TOKEN, or both CV_USERNAME and CV_PASSWORD")
        return self


def default_config_dir() -> Path:
    return Path(os.environ.get("CV_LAB_CONFIG_DIR") or "config")


def commcell_env_path(commcell: str, config_dir: Path) -> Path:
    return config_dir / f"{commcell}.env"


def load_settings(commcell: str, config_dir: Path) -> LabSettings:
    env = commcell_env_path(commcell, config_dir)
    if not env.is_file():
        raise FileNotFoundError(
            f"{env} not found - copy config/commcell.env.example to it, or point "
            "--config-dir / CV_LAB_CONFIG_DIR at the directory that has it."
        )
    return LabSettings(_env_file=env)  # type: ignore[call-arg]
