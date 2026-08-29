"""Track 2 refusals: one exception type, one public projection, no free text.

## Executive summary (read this first)

Every way a Track 2 submission can be refused ends here, as a `T2Refusal` carrying

* a **frozen public C4 code** from `qfbench2_common.contracts.FailureCode` (the closed
  eleven-value enum — this module never invents a twelfth), and
* a **counts-only public detail**, validated by the Hub's shared
  `qfbench2_common.contracts.validate_public_detail`, and
* an **operator reason string** that never leaves an organizer-only sink.

The split is the point. Two live leaks were measured in Track 2's refusal path:
`_g2_cutoff_resource` returned `{"asof": asof, "targets": targets}` — the card's sealed target
dates — into `GateResult.detail`, and the private final scorer logged that dict at ERROR and
returned it inside `error`. The CodaBench driver's private `_WHY_KEYS` allowlist dropped it on one
path and nothing dropped it on the other. So the redaction is no longer a property of *which
entrypoint you happen to be on*: a refusal cannot be constructed with a public detail that carries
free text, because `public_detail()` below runs the Hub validator and raises if it does.

`resolves_after` is gone from the Hub allowlist. This module does not reintroduce an equivalent
channel: the only public-detail values are non-negative integers and one enum code, so there is no
key that can hold a date, an identifier, a path or a parser message.

**Organizer faults are not in this module.** They raise `qfbench2_common.contracts.OrganizerFault`
and abort the evaluation (frozen C1 `organizer_failure.policy = abort_whole_evaluation`). Charging
a broken reference bundle to a participant would turn an organizer defect into somebody's `W`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from qfbench2_common.contracts import (
    FailureCode,
    OrganizerFault,
    validate_public_detail,
)
from qfbench2_common.failure_labels import FailureLabel

__all__ = [
    "LABEL_FOR_CODE",
    "T2Refusal",
    "organizer_fault",
    "public_detail",
]


#: The Track 2 diagnostic label carried alongside each public code.
#:
#: Labels are the cross-track failure-mode taxonomy and are *richer* than the eleven public codes
#: on purpose — the post-competition paper is regenerated from them. They are operator-side: a
#: label never reaches a participant artifact, only its `FailureCode` does.
LABEL_FOR_CODE: Final[Mapping[FailureCode, FailureLabel]] = {
    FailureCode.NO_OUTPUT: FailureLabel.SCHEMA_INVALID_OUTPUT,
    FailureCode.MALFORMED_OUTPUT: FailureLabel.SCHEMA_INVALID_OUTPUT,
    FailureCode.SCHEMA_INVALID: FailureLabel.SCHEMA_INVALID_OUTPUT,
    FailureCode.INCOMPLETE_OUTPUT: FailureLabel.SCHEMA_INVALID_OUTPUT,
    FailureCode.RESOURCE_TIMEOUT: FailureLabel.RESOURCE_TIMEOUT,
    FailureCode.RESOURCE_OOM: FailureLabel.RESOURCE_OOM,
    FailureCode.CONTAINER_CRASHED: FailureLabel.SCHEMA_INVALID_OUTPUT,
    FailureCode.IMAGE_UNUSABLE: FailureLabel.INTEGRITY_BAD_IMAGE_HASH,
    FailureCode.NETWORK_VIOLATION: FailureLabel.LEAKAGE_NETWORK,
    FailureCode.CUTOFF_VIOLATION: FailureLabel.LEAKAGE_CUTOFF,
    FailureCode.CONTAMINATION_DETECTED: FailureLabel.CONTAMINATION_CANARY,
}


def public_detail(code: FailureCode, **counts: int) -> dict[str, Any]:
    """Build the participant-visible `detail`: the enum code plus non-negative integer counts.

    Delegates the allowlist to `qfbench2_common.contracts.validate_public_detail`, so Track 2
    cannot drift from the frozen C4 projection by keeping its own copy of the key list. A caller
    that passes a key outside the allowlist, or a value that is not a non-negative integer, gets a
    `ContractError` **here**, at construction — not a silently dropped field at serialization time.
    Loud is correct: a dropped field is a diagnostic the operator thinks they have and do not.
    """
    payload: dict[str, Any] = {"code": code.value}
    payload.update(counts)
    validated: dict[str, Any] = validate_public_detail(payload)
    return validated


class T2Refusal(Exception):
    """A participant submission is refused. Carries a public code, public counts, and a reason.

    `reason` is operator-only. It exists because an organizer debugging a refused submission needs
    more than `schema_invalid`, and the alternative to a named operator channel is somebody
    stuffing prose into the public detail — which is exactly how a sealed target date reached
    `GateResult.detail` before the freeze.

    `str(self)` deliberately returns the **reason**, so an accidental `print(exc)` on an operator
    path is informative — and every public path uses `.detail`, never `str()`. `public_mapping()`
    is the only thing a participant-visible artifact may serialize.
    """

    __slots__ = ("code", "detail", "reason")

    def __init__(self, code: FailureCode, reason: str, **counts: int) -> None:
        self.code = code
        self.reason = reason
        self.detail = public_detail(code, **counts)
        super().__init__(reason)

    @property
    def label(self) -> FailureLabel:
        return LABEL_FOR_CODE[self.code]

    def public_mapping(self) -> dict[str, Any]:
        """Everything a participant may see about this refusal: `{code, detail}`. Nothing else."""
        return {"failure_code": self.code.value, "detail": dict(self.detail)}


def organizer_fault(reason: str) -> OrganizerFault:
    """Build the organizer-fault exception, so the two fault domains read differently at call sites.

    Returned rather than raised so the caller writes `raise organizer_fault(...)` and a reader
    sees the `raise` at the point it happens.
    """
    return OrganizerFault(reason)
