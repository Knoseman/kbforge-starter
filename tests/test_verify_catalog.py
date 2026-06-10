#!/usr/bin/env python3
"""Unit tests for 01 Reference/scripts/verify_catalog.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "01 Reference" / "scripts"))

import verify_catalog as vc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ARTICLE_FULL = Path(__file__).parent / "fixtures" / "article_full.md"
ARTICLE_MISSING_ANSWER = Path(__file__).parent / "fixtures" / "article_missing_answer.md"
ARTICLE_KNOWN_ISSUE = Path(__file__).parent / "fixtures" / "article_known_issue.md"
ARTICLE_PROCESS_NO_PROC = Path(__file__).parent / "fixtures" / "article_process_no_procedure.md"
TOPICS_VALID = Path(__file__).parent / "fixtures" / "topics_valid.yaml"

FM_BASIC = """---
id: test-article
title: Test Article
kind: reference
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "A test article"
---

## Answer
The answer.
"""

FM_MISSING_REQUIRED = """---
id: incomplete
title: Incomplete
---

## Answer
Body.
"""

FM_ID_MISMATCH = """---
id: wrong-name
title: Mismatch
kind: reference
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "Wrong id"
---

## Answer
Body.
"""

FM_INVALID_KIND = """---
id: bad-kind
title: Bad Kind
kind: nonexistent
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "Bad kind"
---

## Answer
Body.
"""

FM_INVALID_DOMAIN = """---
id: bad-domain
title: Bad Domain
kind: reference
domain: nonexistent
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "Bad domain"
---

## Answer
Body.
"""

FM_INVALID_STATUS = """---
id: bad-status
title: Bad Status
kind: reference
domain: acme-api
topics: [authentication]
status: nonexistent
updated: "2024-01-01"
owner: ai
summary: "Bad status"
---

## Answer
Body.
"""

FM_INVALID_OWNER = """---
id: bad-owner
title: Bad Owner
kind: reference
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: nonexistent
summary: "Bad owner"
---

## Answer
Body.
"""

FM_KNOWN_ISSUE_NO_REVIEW = """---
id: bad-issue
title: Bad Issue
kind: known-issue
domain: ops
topics: [bug]
status: current
updated: "2024-01-01"
owner: ai
summary: "Missing review_due"
---

## Answer
Body.

## Status
Open.
"""

FM_PROVISIONAL_NO_REVIEW = """---
id: bad-prov
title: Bad Provisional
kind: reference
domain: acme-api
topics: [authentication]
status: provisional
updated: "2024-01-01"
owner: ai
summary: "Missing review_due"
---

## Answer
Body.
"""

FM_PROCESS_NO_PROCEDURE = """---
id: bad-process
title: Bad Process
kind: process
domain: ops
topics: [workflow]
status: current
updated: "2024-01-01"
owner: ai
summary: "Missing procedure"
---

## Answer
Body.
"""

FM_KNOWN_ISSUE_NO_STATUS = """---
id: bad-issue-status
title: Bad Issue Status
kind: known-issue
domain: ops
topics: [bug]
status: current
updated: "2024-01-01"
review_due: "2024-06-01"
owner: ai
summary: "Missing status section"
---

## Answer
Body.
"""

FM_INVALID_TOPIC = """---
id: bad-topic
title: Bad Topic
kind: reference
domain: acme-api
topics: [nonexistent-topic]
status: current
updated: "2024-01-01"
owner: ai
summary: "Bad topic"
---

## Answer
Body.
"""

FM_ORPHAN_RELATED = """---
id: orphan
title: Orphan
kind: reference
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "Orphan related"
related: [does-not-exist]
---

## Answer
Body.
"""

BODY_WITH_ANSWER = "## Answer\nYes.\n"
BODY_WITHOUT_ANSWER = "## Overview\nNo.\n"
BODY_WITH_PROCEDURE = "## Answer\nYes.\n\n## Procedure\n1. Step\n"
BODY_WITHOUT_PROCEDURE = "## Answer\nYes.\n"
BODY_WITH_STATUS = "## Answer\nYes.\n\n## Status\nOpen.\n"
BODY_WITHOUT_STATUS = "## Answer\nYes.\n"
BODY_SUBSECTION_FALSE_POSITIVE = "## Overview\n### Answer\nNo.\n\n## Answer\nYes.\n"

TOPICS_YAML_INLINE_COMMENT = """domains:
  - acme-api  # our API
  - ops       # operations

kinds:
  - reference
  - known-issue

statuses:
  - current
  - outdated

owners:
  - ai
  - user

topics:
  - authentication
  - bug
"""

TOPICS_YAML_MISSING_KINDS = """domains:
  - acme-api
"""


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter(unittest.TestCase):
    """Tests for the YAML frontmatter parser in verify_catalog.py."""

    def test_basic(self):
        meta, body = vc.parse_frontmatter(FM_BASIC)
        self.assertEqual(meta["id"], "test-article")
        self.assertEqual(meta["title"], "Test Article")
        self.assertEqual(meta["topics"], ["authentication"])

    def test_multiline_list(self):
        text = """---
id: multi
topics:
  - a
  - b
---

Body.
"""
        meta, _ = vc.parse_frontmatter(text)
        self.assertEqual(meta["topics"], ["a", "b"])

    def test_no_frontmatter(self):
        meta, body = vc.parse_frontmatter(BODY_WITH_ANSWER)
        self.assertEqual(meta, {})
        self.assertEqual(body, BODY_WITH_ANSWER)

    def test_malformed_no_closing(self):
        text = "---\nid: no-close\n"
        meta, body = vc.parse_frontmatter(text)
        self.assertEqual(meta, {})
        self.assertEqual(body, text)


# ---------------------------------------------------------------------------
# _strip_inline_comment
# ---------------------------------------------------------------------------

class TestStripInlineComment(unittest.TestCase):
    """Tests for _strip_inline_comment."""

    def test_no_comment(self):
        self.assertEqual(vc._strip_inline_comment("  - authentication"), "  - authentication")

    def test_inline_comment(self):
        self.assertEqual(vc._strip_inline_comment("  - authentication  # our API"), "  - authentication")

    def test_comment_with_quotes(self):
        """# inside quoted strings should be preserved."""
        self.assertEqual(vc._strip_inline_comment('  - "auth # token"  # comment'), '  - "auth # token"')

    def test_full_line_comment(self):
        # _strip_inline_comment strips # at start of string (position 0 has no preceding space)
        # because the condition is: ch == "#" and not in_q and (i == 0 or s[i-1] in (" ", "\t"))
        self.assertEqual(vc._strip_inline_comment("# this is a comment"), "")
        # The function doesn't strip full-line comments; that's handled by the caller

    def test_hash_in_middle_no_space(self):
        self.assertEqual(vc._strip_inline_comment("  - auth#token"), "  - auth#token")


# ---------------------------------------------------------------------------
# parse_topics_yaml
# ---------------------------------------------------------------------------

class TestParseTopicsYaml(unittest.TestCase):
    """Tests for parse_topics_yaml."""

    def test_valid_file(self):
        result = vc.parse_topics_yaml(TOPICS_VALID)
        self.assertEqual(result["domains"], ["acme-api", "ops"])
        self.assertEqual(result["kinds"], ["reference", "known-issue", "process"])
        self.assertEqual(result["statuses"], ["current", "outdated", "provisional"])
        self.assertEqual(result["owners"], ["ai", "user"])
        self.assertEqual(result["topics"], ["authentication", "endpoints", "bug", "workflow"])

    def test_inline_comments(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(TOPICS_YAML_INLINE_COMMENT)
            path = Path(f.name)
        try:
            result = vc.parse_topics_yaml(path)
            self.assertEqual(result["domains"], ["acme-api", "ops"])
            self.assertEqual(result["topics"], ["authentication", "bug"])
        finally:
            path.unlink()

    def test_empty_sections(self):
        text = """domains:
kinds:
  - reference
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(text)
            path = Path(f.name)
        try:
            result = vc.parse_topics_yaml(path)
            self.assertEqual(result["domains"], [])
            self.assertEqual(result["kinds"], ["reference"])
        finally:
            path.unlink()


# ---------------------------------------------------------------------------
# has_section
# ---------------------------------------------------------------------------

class TestHasSection(unittest.TestCase):
    """Tests for has_section."""

    def test_has_answer(self):
        self.assertTrue(vc.has_section(BODY_WITH_ANSWER, "Answer"))

    def test_missing_answer(self):
        self.assertFalse(vc.has_section(BODY_WITHOUT_ANSWER, "Answer"))

    def test_has_procedure(self):
        self.assertTrue(vc.has_section(BODY_WITH_PROCEDURE, "Procedure"))

    def test_missing_procedure(self):
        self.assertFalse(vc.has_section(BODY_WITHOUT_PROCEDURE, "Procedure"))

    def test_has_status(self):
        self.assertTrue(vc.has_section(BODY_WITH_STATUS, "Status"))

    def test_subsection_false_positive(self):
        """### Answer must NOT match ## Answer."""
        self.assertTrue(vc.has_section(BODY_SUBSECTION_FALSE_POSITIVE, "Answer"))
        # But it should NOT match just the subsection
        body_only_subsection = "## Overview\n### Answer\nNo.\n"
        self.assertFalse(vc.has_section(body_only_subsection, "Answer"))


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------

class TestVerify(unittest.TestCase):
    """Tests for the main verify() function."""

    def _setup_dirs(self, tmp: str, articles: dict[str, str], catalog: list[dict] | None = None):
        """Helper: create articles dir, topics.yaml, and optional catalog.jsonl."""
        tmp_path = Path(tmp)
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()

        for name, content in articles.items():
            (articles_dir / name).write_text(content)

        topics_path = tmp_path / "topics.yaml"
        topics_path.write_text(TOPICS_VALID.read_text())

        catalog_path = tmp_path / "catalog.jsonl"
        if catalog is not None:
            with open(catalog_path, "w") as f:
                for entry in catalog:
                    f.write(json.dumps(entry) + "\n")

        return articles_dir, topics_path, catalog_path

    def test_valid_article_no_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, catalog_path = self._setup_dirs(
                tmp,
                {"test-article.md": FM_BASIC},
                catalog=[{"id": "test-article"}],
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", catalog_path):
                        errors, warnings = vc.verify()

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_missing_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"incomplete.md": FM_MISSING_REQUIRED},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("missing required fields" in e for e in errors))
            missing_fields = next(e for e in errors if "missing required fields" in e)
            self.assertIn("kind", missing_fields)
            self.assertIn("domain", missing_fields)

    def test_id_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"mismatch.md": FM_ID_MISMATCH},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("does not equal filename" in e for e in errors))

    def test_invalid_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-kind.md": FM_INVALID_KIND},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("kind 'nonexistent' not in topics.yaml" in e for e in errors))

    def test_invalid_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-domain.md": FM_INVALID_DOMAIN},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("domain 'nonexistent' not in topics.yaml" in e for e in errors))

    def test_invalid_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-status.md": FM_INVALID_STATUS},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("status 'nonexistent' not in topics.yaml" in e for e in errors))

    def test_invalid_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-owner.md": FM_INVALID_OWNER},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("owner 'nonexistent' not in topics.yaml" in e for e in errors))

    def test_known_issue_missing_review_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-issue.md": FM_KNOWN_ISSUE_NO_REVIEW},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("requires review_due" in e for e in errors))

    def test_provisional_missing_review_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-prov.md": FM_PROVISIONAL_NO_REVIEW},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("requires review_due" in e for e in errors))

    def test_missing_answer_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"no-answer.md": FM_PROCESS_NO_PROCEDURE.replace("kind: process", "kind: reference")},
            )
            # Replace to make it reference but remove Answer section
            text = """---
id: no-answer
title: No Answer
kind: reference
domain: acme-api
topics: [authentication]
status: current
updated: "2024-01-01"
owner: ai
summary: "No answer"
---

## Overview
No answer here.
"""
            (articles_dir / "no-answer.md").write_text(text)

            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("missing ## Answer section" in e for e in errors))

    def test_process_missing_procedure_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-process.md": FM_PROCESS_NO_PROCEDURE},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("kind:process should have ## Procedure" in w for w in warnings))
            # Should NOT be an error
            self.assertFalse(any("kind:process" in e for e in errors))

    def test_known_issue_missing_status_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-issue-status.md": FM_KNOWN_ISSUE_NO_STATUS},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("kind:known-issue should have ## Status" in w for w in warnings))
            self.assertFalse(any("kind:known-issue should have ## Status" in e for e in errors))

    def test_invalid_topic_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"bad-topic.md": FM_INVALID_TOPIC},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("topic 'nonexistent-topic' not in topics.yaml" in w for w in warnings))
            self.assertFalse(any("nonexistent-topic" in e for e in errors))

    def test_orphan_related_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"orphan.md": FM_ORPHAN_RELATED},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("related id 'does-not-exist' does not exist" in e for e in errors))

    def test_catalog_missing_entry_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, catalog_path = self._setup_dirs(
                tmp,
                {"good.md": FM_BASIC},
                catalog=[],  # Empty catalog
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", catalog_path):
                        errors, warnings = vc.verify()

            self.assertTrue(any("missing entry for 'test-article'" in w for w in warnings))

    def test_catalog_orphan_entry_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, catalog_path = self._setup_dirs(
                tmp,
                {"good.md": FM_BASIC},
                catalog=[{"id": "test-article"}, {"id": "orphan-entry"}],
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", catalog_path):
                        errors, warnings = vc.verify()

            self.assertTrue(any("orphan entry 'orphan-entry'" in e for e in errors))

    def test_catalog_jsonl_parse_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, catalog_path = self._setup_dirs(
                tmp,
                {"good.md": FM_BASIC},
            )
            catalog_path.write_text("not valid json\n")

            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", catalog_path):
                        errors, warnings = vc.verify()

            self.assertTrue(any("JSON parse error" in e for e in errors))

    def test_no_catalog_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"good.md": FM_BASIC},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("catalog.jsonl does not exist" in w for w in warnings))

    def test_topics_yaml_missing_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir = Path(tmp) / "articles"
            articles_dir.mkdir()
            (articles_dir / "good.md").write_text(FM_BASIC)

            topics_path = Path(tmp) / "topics.yaml"
            topics_path.write_text(TOPICS_YAML_MISSING_KINDS)

            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertTrue(any("missing 'domains' or 'kinds'" in e for e in errors))

    def test_known_issue_with_review_due_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir, topics_path, _ = self._setup_dirs(
                tmp,
                {"good-issue.md": ARTICLE_KNOWN_ISSUE.read_text()},
            )
            with patch.object(vc, "ARTICLES_DIR", articles_dir):
                with patch.object(vc, "TOPICS_YAML", topics_path):
                    with patch.object(vc, "CATALOG_JSONL", Path(tmp) / "nonexistent"):
                        errors, warnings = vc.verify()

            self.assertFalse(any("requires review_due" in e for e in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
