"""The Commvault client a CommCell's settings describe, with renewed
tokens written back to its .env file under a lock - the same way blt
connects, so the lab and blt can share a token file safely."""

from __future__ import annotations

from pathlib import Path

from commvault_sdk import CommvaultClient, TokenSet

from .lock import wait_lock
from .settings import LabSettings, commcell_env_path
from .tokens import env_token_saver, read_tokens, warn_if_regeneration_due


def commvault_client(
    settings: LabSettings,
    commcell: str,
    config_dir: Path,
    *,
    allow_changes: bool = False,
) -> CommvaultClient:
    tokens = None
    if settings.cv_access_token:
        tokens = TokenSet(
            access_token=settings.cv_access_token.get_secret_value(),
            refresh_token=(
                settings.cv_refresh_token.get_secret_value() if settings.cv_refresh_token else None
            ),
            expires_at=settings.cv_token_expires_at,
            renewable_until=settings.cv_token_renewable_until,
        )
        warn_if_regeneration_due(commcell, settings.cv_token_renewable_until)
    token_file = commcell_env_path(commcell, config_dir)
    # The same lock file name blt uses, beside the token file, so a lab
    # run and a blt run pointed at one file take turns renewing it.
    lock_file = token_file.with_name(f".{token_file.stem}.token.lock")
    return CommvaultClient(
        base_url=settings.cv_base_url,
        username=settings.cv_username,
        password=settings.cv_password.get_secret_value() if settings.cv_password else None,
        access_token=tokens,
        on_token_renew=env_token_saver(token_file),
        token_reload=lambda: read_tokens(token_file),
        token_renew_lock=lambda: wait_lock(lock_file),
        verify_tls=settings.cv_verify_tls,
        ca_bundle=settings.cv_ca_bundle,
        page_size=settings.cv_page_size,
        timeout=settings.cv_timeout_seconds,
        allow_changes=allow_changes,
        deployment=settings.cv_deployment,
        max_calls_per_hour=settings.cv_max_calls_per_hour,
    )
