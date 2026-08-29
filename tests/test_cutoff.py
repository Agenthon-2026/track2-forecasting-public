"""T2-6: staged panels and text corpora are checked against the trusted cutoff, both directions.

`scan_panel_cutoff` and `scan_text_corpus_cutoff` are the checks that never ran. Before the freeze
g2 compared two strings out of metadata; **no staged panel row was ever read**, and the corpus
check returned clean when `corpus_index.json` was absent and trusted the index when it was present.

They live in the canonical package and are called from the private staging gate stack, because the
scoring program never sees the participant mount: under the frozen topology it receives `input/ref`
and `input/res` and nothing else. A check placed where its inputs do not exist is a check that
silently passes.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from conftest import ASOF, build_unit, write_panels, write_parquet, write_text_corpus
from qfbench2_common.contracts import OrganizerFault

from qfbench2_track_forecasting.cutoff import (
    scan_panel_cutoff,
    scan_text_corpus_cutoff,
    trusted_asof,
)

# --------------------------------------------------------------------------- panels


def test_positive_control_clean_panels_pass(tmp_path: pathlib.Path) -> None:
    unit = build_unit(tmp_path / "unit")
    verdict = scan_panel_cutoff(unit / "panels", ASOF)
    assert verdict.panel_count == 1
    assert verdict.late_rows == 0
    assert verdict.scanned_rows == 3


def test_a_panel_row_after_the_asof_is_refused(tmp_path: pathlib.Path) -> None:
    unit = tmp_path / "unit"
    write_panels(unit, late_row=True)
    with pytest.raises(OrganizerFault) as exc:
        scan_panel_cutoff(unit / "panels", ASOF)
    assert "post-date" in str(exc.value)


def test_a_panel_with_no_date_column_is_refused_not_skipped(tmp_path: pathlib.Path) -> None:
    panels = tmp_path / "panels"
    write_parquet(
        panels / "syn.parquet",
        {"asset": ["SYN-A"], "value": [1.0], "panel_id": ["syn"]},
    )
    with pytest.raises(OrganizerFault) as exc:
        scan_panel_cutoff(panels, ASOF)
    assert "never skipped" in str(exc.value)


def test_a_panel_with_a_malformed_date_is_refused(tmp_path: pathlib.Path) -> None:
    panels = tmp_path / "panels"
    write_parquet(
        panels / "syn.parquet",
        {
            "asset": ["SYN-A"],
            "date": ["not-a-date"],
            "panel_id": ["syn"],
            "value": [1.0],
        },
    )
    with pytest.raises(OrganizerFault):
        scan_panel_cutoff(panels, ASOF)


def test_an_empty_panel_directory_is_refused(tmp_path: pathlib.Path) -> None:
    panels = tmp_path / "panels"
    panels.mkdir()
    with pytest.raises(OrganizerFault):
        scan_panel_cutoff(panels, ASOF)


def test_a_stray_non_parquet_file_in_panels_is_refused(tmp_path: pathlib.Path) -> None:
    unit = tmp_path / "unit"
    write_panels(unit)
    (unit / "panels" / "notes.txt").write_text("hello", encoding="utf-8")
    with pytest.raises(OrganizerFault):
        scan_panel_cutoff(unit / "panels", ASOF)


def test_a_missing_panel_directory_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(OrganizerFault):
        scan_panel_cutoff(tmp_path / "absent", ASOF)


# --------------------------------------------------------------------------- text corpus


def test_positive_control_clean_corpus_passes(tmp_path: pathlib.Path) -> None:
    unit = tmp_path / "unit"
    write_text_corpus(unit)
    verdict = scan_text_corpus_cutoff(unit / "text", ASOF)
    assert verdict.indexed_documents == 1
    assert verdict.files_on_disk == 1


def test_a_missing_index_is_a_hard_failure_not_a_clean_verdict(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "doc-1.md").write_text("hello", encoding="utf-8")
    with pytest.raises(OrganizerFault) as exc:
        scan_text_corpus_cutoff(corpus, ASOF)
    assert "absence of a check" in str(exc.value)


def test_an_unindexed_document_is_refused(tmp_path: pathlib.Path) -> None:
    """One-directional coverage: the file exists, the index does not mention it, nothing checked it."""
    unit = tmp_path / "unit"
    write_text_corpus(unit, extra_unindexed=True)
    with pytest.raises(OrganizerFault) as exc:
        scan_text_corpus_cutoff(unit / "text", ASOF)
    assert "unindexed" in str(exc.value)


def test_an_indexed_document_absent_from_disk_is_refused(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "doc-1.md").write_text("hello", encoding="utf-8")
    (corpus / "corpus_index.json").write_text(
        json.dumps(
            {
                "documents": [
                    {"doc_id": "doc-1", "path": "doc-1.md", "timestamp": "2020-06-01"},
                    {"doc_id": "doc-9", "path": "doc-9.md", "timestamp": "2020-06-01"},
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(OrganizerFault):
        scan_text_corpus_cutoff(corpus, ASOF)


def test_a_post_asof_document_is_refused(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "doc-1.md").write_text("hello", encoding="utf-8")
    (corpus / "corpus_index.json").write_text(
        json.dumps(
            {"documents": [{"doc_id": "doc-1", "path": "doc-1.md", "timestamp": "2021-01-01"}]}
        ),
        encoding="utf-8",
    )
    with pytest.raises(OrganizerFault) as exc:
        scan_text_corpus_cutoff(corpus, ASOF)
    assert "look-ahead" in str(exc.value)


def test_an_undated_document_is_refused(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "doc-1.md").write_text("hello", encoding="utf-8")
    (corpus / "corpus_index.json").write_text(
        json.dumps({"documents": [{"doc_id": "doc-1", "path": "doc-1.md"}]}),
        encoding="utf-8",
    )
    with pytest.raises(OrganizerFault) as exc:
        scan_text_corpus_cutoff(corpus, ASOF)
    assert "not assumed to be in range" in str(exc.value)


def test_an_empty_documents_array_is_refused(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "corpus_index.json").write_text(json.dumps({"documents": []}), encoding="utf-8")
    with pytest.raises(OrganizerFault):
        scan_text_corpus_cutoff(corpus, ASOF)


# --------------------------------------------------------------------------- asof resolution


def test_trusted_asof_reads_provenance_data_cutoff() -> None:
    assert trusted_asof({"provenance": {"data_cutoff": "2020-06-30"}}) == "2020-06-30"


def test_trusted_asof_prefers_forecast_asof() -> None:
    card = {"forecast": {"asof": "2020-01-01"}, "provenance": {"data_cutoff": "2020-06-30"}}
    assert trusted_asof(card) == "2020-01-01"


def test_a_card_with_no_asof_is_an_organizer_fault() -> None:
    with pytest.raises(OrganizerFault):
        trusted_asof({"task": {"id": "t2-SYN-0001"}})


def test_a_malformed_asof_is_an_organizer_fault() -> None:
    with pytest.raises(OrganizerFault):
        trusted_asof({"provenance": {"data_cutoff": "June 2020"}})


def test_no_refusal_message_repeats_a_document_id(tmp_path: pathlib.Path) -> None:
    """Corpus doc ids are organizer material. Refusals carry counts, not identifiers."""
    corpus = tmp_path / "text"
    corpus.mkdir()
    (corpus / "sealed-doc-name.md").write_text("hello", encoding="utf-8")
    (corpus / "corpus_index.json").write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "doc_id": "SEALED-DOC-ID",
                        "path": "sealed-doc-name.md",
                        "timestamp": "2021-01-01",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(OrganizerFault) as exc:
        scan_text_corpus_cutoff(corpus, ASOF)
    assert "SEALED-DOC-ID" not in str(exc.value)
    assert "sealed-doc-name" not in str(exc.value)
