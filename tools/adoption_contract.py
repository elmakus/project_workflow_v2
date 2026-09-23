#!/usr/bin/env python3
"""Deterministic first-adoption/custody-transfer safety contract."""

from __future__ import annotations


class AdoptionContractError(ValueError):
    pass


def custody_transfer_action(
    *,
    explicit_authorization: bool,
    package_verified: bool,
    terminal_handoff_present: bool,
    source_owner_active: bool,
    destination_owner_active: bool,
    package_subject: str,
    handoff_package_subject: str = "",
) -> str:
    """Choose the only safe next action for the one-time V1 -> V2 custody transfer.

    Cross-repository writes are not atomic. The source remains the sole live owner
    until a verified V2 package is ready and an explicit adoption authorization is
    present. Once the terminal source handoff is written, the source is retired;
    if destination activation was interrupted, recovery resumes from that exact
    handoff/package subject rather than guessing or reactivating the source.
    """

    if not package_subject.strip():
        raise AdoptionContractError("custody transfer requires an exact V2 package subject")

    if not explicit_authorization:
        return "authorization_stop"

    if source_owner_active and destination_owner_active:
        raise AdoptionContractError("custody is ambiguous: both source and destination are mutable")

    if not terminal_handoff_present:
        if destination_owner_active:
            raise AdoptionContractError(
                "destination cannot become live before the terminal source handoff"
            )
        if not source_owner_active:
            raise AdoptionContractError(
                "custody is ambiguous: source retired before a terminal transfer handoff"
            )
        if not package_verified:
            return "stage_and_verify_package"
        return "record_terminal_transfer"

    if not handoff_package_subject.strip():
        raise AdoptionContractError(
            "terminal transfer handoff must identify the exact V2 package subject"
        )
    if handoff_package_subject != package_subject:
        raise AdoptionContractError(
            "terminal transfer handoff does not match the verified V2 package subject"
        )
    if not package_verified:
        raise AdoptionContractError(
            "terminal transfer handoff cannot rely on an unverified V2 package"
        )
    if source_owner_active:
        raise AdoptionContractError(
            "terminal transfer handoff requires the V1 source owner to be retired"
        )
    if destination_owner_active:
        return "transferred_verified"
    return "activate_destination_from_terminal_handoff"
