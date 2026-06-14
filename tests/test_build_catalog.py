#!/usr/bin/env python3
"""Unit tests for 01 Reference/scripts/build_catalog.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "01 Reference" / "scripts"))

import build_catalog as bc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ARTICLE_FULL = Path(__file__).parent / "fixtures" / "article_full.md"
ARTICLE_MISSING_ANSWER = Path(__file__).parent / "fixtures" / "article_missing_answer.md"

FM_BASIC = """---
id: test-article
title: Test Article
kind: reference
domain: acme-api
topics: [authentication, endpoints]
status: current
updated: "2024-01-01"
owner: ai
summary: "A test article"
answers: ["How does it work?"]
related: [other-article]
created_by: tester
---

## Answer
The answer is here.

## Status
All good.
"""

FM_INLINE_LIST = """---
id: inline
title: Inline
topics: ["a", "b"]
answers: ["q1", "q2"]
---

Body.
"""

FM_NO_FRONTMATTER = "No frontmatter here.\n\n## Answer\nContent.\n"

FM_EMPTY = ""

FM_MULTILINE_TOPICS = """---
id: multi
title: Multi
topics:
  - authentication
  - endpoints
---

Body.
"""

FM_SUPERCEDED = """---
id: old
title: Old Article
superseded_by: new-article
---

Body.
"""

BODY_WITH_SECTIONS = """## Answer
First paragraph.

Second paragraph.

## Status
Current.

## Procedure
1. One
2. Two
"""

BODY_NO_ANSWER = """## Overview
No answer here.

## Status
Current.
"""

BODY_SUBSECTION_FALSE_POSITIVE = """## Overview
### Answer
This is a subsection, not the real Answer section.

## Answer
This is the real answer.
"""


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter(unittest.TestCase):
    """Tests for the YAML frontmatter parser in build_catalog.py."""

    def test_no_frontmatter(self):
        meta, body = bc.parse_frontmatter(FM_NO_FRONTMATTER)
        self.assertEqual(meta, {})
        self.assertEqual(body, FM_NO_FRONTMATTER)

    def test_empty_string(self):
        meta, body = bc.parse_frontmatter(FM_EMPTY)
        self.assertEqual(meta, {})
        self.assertEqual(body, "")

    def test_basic_key_value(self):
        meta, body = bc.parse_frontmatter(FM_BASIC)
        self.assertEqual(meta["id"], "test-article")
        self.assertEqual(meta["title"], "Test Article")
        self.assertEqual(meta["kind"], "reference")
        self.assertEqual(meta["domain"], "acme-api")
        self.assertEqual(meta["status"], "current")
        self.assertEqual(meta["owner"], "ai")
        self.assertEqual(meta["summary"], "A test article")
        self.assertEqual(meta["created_by"], "tester")

    def test_inline_list(self):
        meta, _ = bc.parse_frontmatter(FM_INLINE_LIST)
        self.assertEqual(meta["topics"], ["a", "b"])
        self.assertEqual(meta["answers"], ["q1", "q2"])

    def test_multiline_list(self):
        meta, _ = bc.parse_frontmatter(FM_MULTILINE_TOPICS)
        self.assertEqual(meta["topics"], ["authentication", "endpoints"])

    def test_superseded_by(self):
        meta, _ = bc.parse_frontmatter(FM_SUPERCEDED)
        self.assertEqual(meta["superseded_by"], "new-article")

    def test_body_extracted(self):
        meta, body = bc.parse_frontmatter(FM_BASIC)
        self.assertTrue(body.startswith("## Answer"))
        self.assertIn("The answer is here.", body)
        self.assertIn("## Status", body)

    def test_malformed_no_closing(self):
        text = "---\nid: no-close\n"
        meta, body = bc.parse_frontmatter(text)
        self.assertEqual(meta, {})
        self.assertEqual(body, text)

    def test_pipe_value(self):
        """Pipe character as value should create empty list."""
        text = """---
id: pipe-test
topics: |
---

Body.
"""
        meta, _ = bc.parse_frontmatter(text)
        self.assertEqual(meta["topics"], [])


# ---------------------------------------------------------------------------
# extract_section
# ---------------------------------------------------------------------------

class TestExtractSection(unittest.TestCase):
    """Tests for extract_section with re.DOTALL."""

    def test_basic_extraction(self):
        result = bc.extract_section(BODY_WITH_SECTIONS, "Answer")
        self.assertEqual(result, "First paragraph.\n\nSecond paragraph.")

    def test_missing_section(self):
        result = bc.extract_section(BODY_NO_ANSWER, "Answer")
        self.assertEqual(result, "")

    def test_multiline_extraction(self):
        result = bc.extract_section(BODY_WITH_SECTIONS, "Status")
        self.assertEqual(result, "Current.")

    def test_subsection_false_positive(self):
        """### Answer must NOT match ## Answer.

        The regex anchors to start of line with ^ and re.MULTILINE, so
        `### Answer` is correctly ignored while `## Answer` is matched.
        """
        result = bc.extract_section(BODY_SUBSECTION_FALSE_POSITIVE, "Answer")
        self.assertEqual(result, "This is the real answer.")
        self.assertNotIn("subsection", result)

    def test_trailing_content(self):
        body = "## Answer\nOnly section.\n"
        result = bc.extract_section(body, "Answer")
        self.assertEqual(result, "Only section.")

    def test_empty_section(self):
        body = "## Answer\n\n## Status\nDone.\n"
        result = bc.extract_section(body, "Answer")
        self.assertEqual(result, "")


# ---------------------------------------------------------------------------
# build_catalog
# ---------------------------------------------------------------------------

class TestBuildCatalog(unittest.TestCase):
    """Tests for build_catalog with mocked article directory."""

    def test_full_article(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            (articles_dir / "article-full.md").write_text(ARTICLE_FULL.read_text())

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                articles = bc.build_catalog()

            self.assertEqual(len(articles), 1)
            art = articles[0]
            self.assertEqual(art["id"], "article-full")
            self.assertEqual(art["title"], "Full Article")
            self.assertEqual(art["kind"], "reference")
            self.assertEqual(art["domain"], "acme-api")
            self.assertEqual(art["topics"], ["authentication", "endpoints"])
            self.assertEqual(art["status"], "current")
            self.assertEqual(art["owner"], "ai")
            self.assertEqual(art["summary"], "A full test article.")
            self.assertEqual(art["answers"], ["How does auth work?"])
            self.assertEqual(art["related"], ["article-minimal"])
            self.assertEqual(art["created_by"], "test")
            self.assertIn("_body", art)
            self.assertIn("_answer", art)
            self.assertIn("_status_section", art)
            self.assertEqual(art["_answer"], "This is the answer section.\nIt spans multiple lines.")
            self.assertEqual(art["_status_section"], "Current and stable.")

    def test_underscore_files_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            (articles_dir / "_draft.md").write_text("---\nid: draft\n---\n\nBody.\n")
            (articles_dir / "public.md").write_text("---\nid: public\n---\n\nBody.\n")

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                articles = bc.build_catalog()

            self.assertEqual(len(articles), 1)
            self.assertEqual(articles[0]["id"], "public")

    def test_missing_id_uses_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            (articles_dir / "from-filename.md").write_text("---\ntitle: No ID\n---\n\nBody.\n")

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                articles = bc.build_catalog()

            self.assertEqual(len(articles), 1)
            self.assertEqual(articles[0]["id"], "from-filename")

    def test_superseded_by_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            (articles_dir / "old.md").write_text(FM_SUPERCEDED)

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                articles = bc.build_catalog()

            self.assertIn("superseded_by", articles[0])
            self.assertEqual(articles[0]["superseded_by"], "new-article")

    def test_no_superseded_by_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            articles_dir.mkdir()
            (articles_dir / "normal.md").write_text("---\nid: normal\ntitle: Normal\n---\n\nBody.\n")

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                articles = bc.build_catalog()

            self.assertNotIn("superseded_by", articles[0])


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

class TestWriteCatalogJsonl(unittest.TestCase):
    """Tests for write_catalog_jsonl."""

    def test_private_fields_stripped(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            jsonl_path = tmp_path / "catalog.jsonl"

            articles = [
                {"id": "a", "title": "A", "_body": "secret", "_answer": "secret2", "empty": ""},
            ]

            with patch.object(bc, "CATALOG_JSONL", jsonl_path):
                bc.write_catalog_jsonl(articles)

            lines = jsonl_path.read_text().strip().split("\n")
            entry = json.loads(lines[0])
            self.assertEqual(entry["id"], "a")
            self.assertNotIn("_body", entry)
            self.assertNotIn("_answer", entry)
            self.assertNotIn("empty", entry)

    def test_falsy_values_filtered(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            jsonl_path = tmp_path / "catalog.jsonl"

            articles = [
                {"id": "a", "title": "", "topics": [], "related": None, "summary": "Has summary"},
            ]

            with patch.object(bc, "CATALOG_JSONL", jsonl_path):
                bc.write_catalog_jsonl(articles)

            lines = jsonl_path.read_text().strip().split("\n")
            entry = json.loads(lines[0])
            self.assertEqual(entry["id"], "a")
            self.assertNotIn("title", entry)
            self.assertNotIn("topics", entry)
            self.assertNotIn("related", entry)
            self.assertEqual(entry["summary"], "Has summary")


class TestWriteCatalogMd(unittest.TestCase):
    """Tests for write_catalog_md."""

    def test_basic_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            md_path = tmp_path / "catalog.md"

            articles = [
                {"id": "a", "title": "A", "kind": "reference", "domain": "api", "summary": "Summary A", "status": "current"},
                {"id": "b", "title": "B", "kind": "troubleshooting", "domain": "ops", "summary": "Summary B", "status": "outdated"},
            ]

            with patch.object(bc, "CATALOG_MD", md_path):
                bc.write_catalog_md(articles)

            text = md_path.read_text(encoding="utf-8")
            self.assertIn("# Reference Catalog", text)
            self.assertIn("## api", text)
            self.assertIn("## ops", text)
            self.assertIn("| `a` | reference | Summary A |", text)
            self.assertIn("| `b`", text)
            self.assertIn("troubleshooting", text)
            self.assertIn("Summary B", text)

    def test_empty_domain_grouped_as_other(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            md_path = tmp_path / "catalog.md"

            articles = [
                {"id": "a", "title": "A", "kind": "reference", "domain": "", "summary": "S", "status": "current"},
            ]

            with patch.object(bc, "CATALOG_MD", md_path):
                bc.write_catalog_md(articles)

            text = md_path.read_text(encoding="utf-8")
            self.assertIn("## other", text)


class TestWriteAggregates(unittest.TestCase):
    """Tests for write_aggregates."""

    def test_known_issues_aggregate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            articles = [
                {
                    "id": "bug-1", "title": "Bug One", "kind": "known-issue",
                    "status": "current", "review_due": "2024-06-01",
                    "_answer": "It crashes.", "_status_section": "Under investigation.",
                    "summary": "A bug",
                },
                {
                    "id": "ref-1", "title": "Ref One", "kind": "reference",
                    "_answer": "", "_status_section": "", "summary": "Not a bug",
                },
            ]

            with patch.object(bc, "AGGREGATES_DIR", agg_dir):
                bc.write_aggregates(articles)

            text = (agg_dir / "known-issues.md").read_text()
            self.assertIn("# Known Issues", text)
            self.assertIn("## Bug One", text)
            self.assertIn("It crashes.", text)
            self.assertIn("Under investigation.", text)
            self.assertNotIn("Ref One", text)

    def test_empty_aggregates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            articles = [
                {"id": "ref-1", "title": "Ref", "kind": "reference", "_answer": "", "_status_section": "", "summary": "S"},
            ]

            with patch.object(bc, "AGGREGATES_DIR", agg_dir):
                bc.write_aggregates(articles)

            # All aggregates should be written even if empty
            self.assertTrue((agg_dir / "known-issues.md").exists())
            self.assertTrue((agg_dir / "contacts.md").exists())
            self.assertTrue((agg_dir / "comparisons.md").exists())
            self.assertTrue((agg_dir / "environments.md").exists())

    def test_environments_by_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            articles = [
                {
                    "id": "env-1", "title": "Env", "kind": "reference",
                    "topics": ["test-environments", "authentication"],
                    "_answer": "Test env details.", "summary": "S",
                },
                {
                    "id": "other", "title": "Other", "kind": "reference",
                    "topics": ["lifecycle"],
                    "_answer": "", "summary": "S",
                },
            ]

            with patch.object(bc, "AGGREGATES_DIR", agg_dir):
                bc.write_aggregates(articles)

            text = (agg_dir / "environments.md").read_text()
            self.assertIn("## Env", text)
            self.assertIn("Test env details.", text)
            self.assertNotIn("## Other", text)


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------

class TestRoundTrip(unittest.TestCase):
    """End-to-end test from articles to all outputs."""

    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            articles_dir = tmp_path / "articles"
            agg_dir = tmp_path / "aggregates"
            jsonl_path = tmp_path / "catalog.jsonl"
            md_path = tmp_path / "catalog.md"

            articles_dir.mkdir()

            (articles_dir / "article-full.md").write_text(ARTICLE_FULL.read_text())
            (articles_dir / "article-missing-answer.md").write_text(ARTICLE_MISSING_ANSWER.read_text())

            with patch.object(bc, "ARTICLES_DIR", articles_dir):
                with patch.object(bc, "AGGREGATES_DIR", agg_dir):
                    with patch.object(bc, "CATALOG_JSONL", jsonl_path):
                        with patch.object(bc, "CATALOG_MD", md_path):
                            articles = bc.build_catalog()
                            bc.write_catalog_jsonl(articles)
                            bc.write_catalog_md(articles)
                            bc.write_aggregates(articles)

            # JSONL
            lines = jsonl_path.read_text().strip().split("\n")
            self.assertEqual(len(lines), 2)
            entries = {json.loads(l)["id"]: json.loads(l) for l in lines}
            self.assertIn("article-full", entries)
            self.assertIn("article-missing-answer", entries)

            # catalog.md
            md_text = md_path.read_text()
            self.assertIn("article-full", md_text)
            self.assertIn("article-missing-answer", md_text)

            # aggregates
            self.assertTrue((agg_dir / "known-issues.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
