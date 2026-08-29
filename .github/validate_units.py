#!/usr/bin/env python3
"""CI unit validator (root-relative).

Validates every public unit in ./units against:
  - card.toml: schema_version == "2.0"; [task] id/track/title/split present (no placeholders);
    [task].track matches the expected track; no private-test unit in a public repo;
  - [contamination].canary_guid present, a valid UUIDv4, and globally unique across units;
  - manifest.json checksums (qfbench2_common.manifest.verify_manifest);
  - public-safety firewall (qfbench2_common.manifest.assert_public_safe) — no oracle/solution leak.

Usage:  python .github/validate_units.py <expected-track> [--stdlib-only]
Exit 0 if all units pass; exit 1 with a list of errors otherwise.

``--stdlib-only`` runs just the card/track/split/canary checks, which need nothing but the
standard library, and skips the two toolkit-backed checks. It exists so the firewall can run
in a job that does not install the shared toolkit. The toolkit installs anonymously from the
public Agenthon2026-public repository, so no credential is involved and this workflow runs on
fork pull requests like any other; what a toolkit install still costs is availability. Steps
after a failed install are SKIPPED, so a firewall placed behind the shared-toolkit install step
silently does not run in exactly the case that matters most -- an unresolvable ref, a bad tag
or a network failure. The skipped checks are named explicitly in the output -- a stdlib-only
pass is not a full validation and must not be read as one.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tomllib

UUID4 = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def main(expected_track: str, stdlib_only: bool = False) -> int:
    root = pathlib.Path("units")
    if not root.is_dir():
        # Previously this fell back to an empty list, so a renamed or missing units/
        # directory printed "All 0 unit(s) valid" and exited 0 -- a validator that
        # reports success having inspected nothing.
        print(f"UNIT VALIDATION ERROR: no {root}/ directory (cwd={pathlib.Path.cwd()})")
        return 1
    units = [u for u in sorted(root.iterdir()) if u.is_dir()]
    if not units:
        print(f"UNIT VALIDATION ERROR: {root}/ contains no unit directories")
        return 1

    verify_manifest = assert_public_safe = None
    if not stdlib_only:
        # Imported lazily so --stdlib-only needs no toolkit install.
        from qfbench2_common.manifest import assert_public_safe, verify_manifest

    errors: list[str] = []
    guids: dict[str, str] = {}

    for u in units:
        card_path = u / "card.toml"
        if not card_path.exists():
            errors.append(f"{u.name}: missing card.toml")
            continue
        try:
            card = tomllib.loads(card_path.read_text())
        except Exception as exc:  # noqa: BLE001 - report any parse failure
            errors.append(f"{u.name}: card.toml parse error: {exc}")
            continue

        if card.get("schema_version") != "2.0":
            errors.append(f"{u.name}: schema_version must be '2.0'")

        task = card.get("task", {})
        for field in ("id", "track", "title", "split"):
            value = str(task.get(field, ""))
            if not value or "<" in value:
                errors.append(f"{u.name}: [task].{field} is empty or a placeholder")
        if task.get("track") != expected_track:
            errors.append(
                f"{u.name}: [task].track must be {expected_track!r}, got {task.get('track')!r}"
            )
        if task.get("split") == "private-test":
            errors.append(f"{u.name}: a private-test unit must never appear in a public repo")

        guid = card.get("contamination", {}).get("canary_guid", "")
        if not guid or not UUID4.match(str(guid).lower()):
            errors.append(f"{u.name}: missing or invalid canary_guid")
        elif guid in guids:
            errors.append(f"{u.name}: duplicate canary_guid (also used by {guids[guid]})")
        else:
            guids[guid] = u.name

        if verify_manifest is not None and assert_public_safe is not None:
            errors.extend(f"{u.name}: manifest: {e}" for e in verify_manifest(u))
            errors.extend(f"{u.name}: public-safety: {e}" for e in assert_public_safe(u))

    # Answer-shaped paths anywhere OUTSIDE units/ (the per-unit firewall above only reaches
    # units/). regression_suite/ carries synthetic fixtures, not units, but a real answer file
    # landing there would still be invisible to this validator without this sweep.
    for extra_root in (pathlib.Path("regression_suite"),):
        if not extra_root.is_dir():
            continue
        for p in extra_root.rglob("*"):
            if not p.is_file():
                continue
            parts = p.parts
            if "reference" in parts or p.name.startswith(("realized", "outcome")):
                errors.append(f"{p.as_posix()}: answer-shaped path outside units/ "
                              "(rename; keep sealed answers out of the tree)")

    if errors:
        print("UNIT VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1
    checked = "schema, track, split, canary uniqueness"
    if stdlib_only:
        print(
            f"All {len(units)} unit(s) pass the stdlib checks: {checked}.\n"
            "NOT CHECKED HERE (they need the shared toolkit, see the validate-units job): "
            "manifest checksums, public-safety firewall."
        )
    else:
        print(
            f"All {len(units)} unit(s) valid: {checked}, "
            "manifest checksums, public-safety."
        )
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    stdlib_only = "--stdlib-only" in args
    positional = [a for a in args if not a.startswith("-")]
    sys.exit(main(positional[0] if positional else "", stdlib_only=stdlib_only))
