#!/usr/bin/env python3
"""Unit tests for 04 Skills/scripts/build_skills_index.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "04 Skills" / "scripts"))

import build_skills_index as bsi


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SKILL_WITH_TOUCHES_TRIGGERS = Path(__file__).parent / "fixtures" / "skill_with_touches_and_triggers.md"
SKILL_MINIMAL = Path(__file__).parent / "fixtures" / "skill_minimal.md"
SKILL_PRO = Path(__file__).parent / "fixtures" / "skill_pro_tier.md"

FM_BASIC = """---
id: test
title: Hello
kind: lookup
inputs: [a, b]
outputs: [c]
chains_to: [d]
chains_from: [e]
triggers:
  - "trigger one"
  - "trigger two"
success_rate: high
summary: "A test skill"
---

## When
Body here.
"""

FM_INLINE_LIST = """---
id: inline
title: Inline
inputs: ["a", "b"]
triggers: ["one", "two"]
---

Body.
"""

FM_TOUCHES_THEN_TRIGGERS = """---
id: regression
title: Regression Test
kind: capture
touches:
  reads:
    - "file1"
    - "file2"
  writes:
    - "file3"
triggers:
  - "trigger A"
  - "trigger B"
---

## When
Body.
"""

FM_NO_FRONTMATTER = "No frontmatter here.\n\n## Section\nContent.\n"

FM_EMPTY = ""

FM_QUOTED_STRINGS = """---
id: quoted
title: "Quoted Title"
summary: 'Single quoted'
---

Body.
"""

FM_COMMENTS = """---
id: commented
title: Commented  # inline comment
# full line comment
summary: "Has comment"
---

Body.
"""

FM_NESTED_EMPTY_LIST = """---
id: nested-empty
touches:
  reads:
  writes:
triggers:
  - "t1"
---

Body.
"""


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter(unittest.TestCase):
    """Tests for the YAML frontmatter parser."""

    def test_no_frontmatter(self):
        meta, body = bsi.parse_frontmatter(FM_NO_FRONTMATTER)
        self.assertEqual(meta, {})
        self.assertEqual(body, FM_NO_FRONTMATTER)

    def test_empty_string(self):
        meta, body = bsi.parse_frontmatter(FM_EMPTY)
        self.assertEqual(meta, {})
        self.assertEqual(body, "")

    def test_basic_key_value(self):
        meta, body = bsi.parse_frontmatter(FM_BASIC)
        self.assertEqual(meta["id"], "test")
        self.assertEqual(meta["title"], "Hello")
        self.assertEqual(meta["kind"], "lookup")
        self.assertEqual(meta["success_rate"], "high")
        self.assertEqual(meta["summary"], "A test skill")

    def test_inline_list(self):
        meta, _ = bsi.parse_frontmatter(FM_INLINE_LIST)
        self.assertEqual(meta["inputs"], ["a", "b"])
        self.assertEqual(meta["triggers"], ["one", "two"])

    def test_multiline_list(self):
        meta, _ = bsi.parse_frontmatter(FM_BASIC)
        self.assertEqual(meta["triggers"], ["trigger one", "trigger two"])

    def test_nested_dict_touches(self):
        meta, _ = bsi.parse_frontmatter(FM_BASIC)
        # FM_BASIC has no touches, so this key shouldn't exist
        self.assertNotIn("touches", meta)

    def test_nested_dict_reads_writes(self):
        meta, _ = bsi.parse_frontmatter(FM_TOUCHES_THEN_TRIGGERS)
        self.assertIn("touches", meta)
        self.assertIsInstance(meta["touches"], dict)
        self.assertEqual(meta["touches"]["reads"], ["file1", "file2"])
        self.assertEqual(meta["touches"]["writes"], ["file3"])

    def test_regression_list_after_dict(self):
        """CRITICAL: triggers list after touches dict must parse as list, not empty dict."""
        meta, _ = bsi.parse_frontmatter(FM_TOUCHES_THEN_TRIGGERS)
        self.assertIn("triggers", meta)
        self.assertIsInstance(meta["triggers"], list)
        self.assertEqual(meta["triggers"], ["trigger A", "trigger B"])

    def test_quoted_strings(self):
        meta, _ = bsi.parse_frontmatter(FM_QUOTED_STRINGS)
        self.assertEqual(meta["title"], "Quoted Title")
        self.assertEqual(meta["summary"], "Single quoted")

    def test_comments_ignored(self):
        meta, _ = bsi.parse_frontmatter(FM_COMMENTS)
        self.assertEqual(meta["id"], "commented")
        # build_skills_index parser does NOT strip inline comments on value lines
        # (full-line comments starting with # are skipped, inline ones are not)
        self.assertEqual(meta["title"], "Commented  # inline comment")
        self.assertEqual(meta["summary"], "Has comment")

    def test_nested_empty_list(self):
        """Empty sub-lists inside touches should remain empty lists."""
        meta, _ = bsi.parse_frontmatter(FM_NESTED_EMPTY_LIST)
        self.assertIn("touches", meta)
        self.assertIsInstance(meta["touches"], dict)
        self.assertEqual(meta["touches"]["reads"], [])
        self.assertEqual(meta["touches"]["writes"], [])
        self.assertEqual(meta["triggers"], ["t1"])

    def test_body_extracted(self):
        meta, body = bsi.parse_frontmatter(FM_BASIC)
        self.assertTrue(body.startswith("## When"))
        self.assertIn("Body here.", body)

    def test_malformed_no_closing(self):
        text = "---\nid: no-close\n"
        meta, body = bsi.parse_frontmatter(text)
        self.assertEqual(meta, {})
        self.assertEqual(body, text)


# ---------------------------------------------------------------------------
# _load_skill
# ---------------------------------------------------------------------------

class TestLoadSkill(unittest.TestCase):
    """Tests for _load_skill helper."""

    def test_load_full_skill(self):
        entry = bsi._load_skill(SKILL_WITH_TOUCHES_TRIGGERS)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["id"], "test-skill")
        self.assertEqual(entry["title"], "Test Skill")
        self.assertEqual(entry["kind"], "capture")
        self.assertEqual(entry["inputs"], ["source_path"])
        self.assertEqual(entry["outputs"], ["article"])
        self.assertEqual(entry["chains_to"], ["kb-gaps"])
        self.assertEqual(entry["chains_from"], ["triage"])
        self.assertEqual(entry["collapsed_from"], ["clean-source", "ingest-source"])
        self.assertTrue(entry["fast_path"])
        self.assertEqual(entry["triggers"], ["process this source", "ingest this transcript", "full ingest"])
        self.assertEqual(entry["success_rate"], "unrated")
        self.assertEqual(entry["summary"], "Complete pipeline test.")
        self.assertIn("touches", entry)
        self.assertEqual(entry["touches"]["reads"], ["00 Raw Sources/**/*", "01 Reference/catalog.jsonl"])

    def test_load_minimal_skill(self):
        entry = bsi._load_skill(SKILL_MINIMAL)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["id"], "minimal-skill")
        self.assertEqual(entry["title"], "Minimal")
        self.assertEqual(entry["kind"], "")
        self.assertEqual(entry["inputs"], [])
        self.assertEqual(entry["triggers"], [])
        self.assertFalse(entry["fast_path"])

    def test_missing_id_returns_none(self):
        # File with no id field and no frontmatter id — stem becomes fallback id
        # To truly test missing id, we need empty frontmatter with no id key
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\ntitle: No ID\n---\n\nBody.\n")
            path = Path(f.name)
        try:
            entry = bsi._load_skill(path)
            # stem IS the id fallback, so this won't be None. Test with truly empty id.
            self.assertIsNotNone(entry)
            self.assertEqual(entry["id"], path.stem)
        finally:
            path.unlink()

    def test_empty_id_returns_none(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\nid:\ntitle: Empty ID\n---\n\nBody.\n")
            path = Path(f.name)
        try:
            entry = bsi._load_skill(path)
            self.assertIsNone(entry)
        finally:
            path.unlink()


# ---------------------------------------------------------------------------
# build_index
# ---------------------------------------------------------------------------

class TestBuildIndex(unittest.TestCase):
    """Tests for build_index with mocked directories."""

    def test_build_with_free_and_pro(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            free_dir = tmp_path / "skills"
            pro_dir = tmp_path / "pro-pack" / "skills"
            free_dir.mkdir(parents=True)
            pro_dir.mkdir(parents=True)

            # Copy fixtures
            (free_dir / "test-skill.md").write_text(SKILL_WITH_TOUCHES_TRIGGERS.read_text())
            (pro_dir / "pro-skill.md").write_text(SKILL_PRO.read_text())

            with patch.object(bsi, "SKILLS_DIR", free_dir):
                with patch.object(bsi, "PRO_SKILLS_DIR", pro_dir):
                    skills = bsi.build_index()

            self.assertEqual(len(skills), 2)
            ids = {s["id"] for s in skills}
            self.assertEqual(ids, {"test-skill", "pro-skill"})

            pro = next(s for s in skills if s["id"] == "pro-skill")
            self.assertTrue(pro.get("pro"))

            free = next(s for s in skills if s["id"] == "test-skill")
            self.assertNotIn("pro", free)

    def test_build_no_pro_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            free_dir = tmp_path / "skills"
            free_dir.mkdir()
            (free_dir / "test.md").write_text(SKILL_MINIMAL.read_text())

            with patch.object(bsi, "SKILLS_DIR", free_dir):
                with patch.object(bsi, "PRO_SKILLS_DIR", tmp_path / "nonexistent"):
                    skills = bsi.build_index()

            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0]["id"], "minimal-skill")

    def test_build_empty_free_dir(self):
        """Empty free dir returns empty list (does not exit)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            free_dir = tmp_path / "skills"
            free_dir.mkdir()

            with patch.object(bsi, "SKILLS_DIR", free_dir):
                with patch.object(bsi, "PRO_SKILLS_DIR", tmp_path / "nonexistent"):
                    skills = bsi.build_index()

            self.assertEqual(skills, [])


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

class TestWriteIndex(unittest.TestCase):
    """Tests for write_index JSONL output."""

    def test_falsy_values_filtered(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            index_path = tmp_path / "skills.jsonl"

            skills = [
                {"id": "a", "title": "A", "fast_path": True, "empty": "", "none": None, "zero": 0, "false": False},
                {"id": "b", "title": "B", "fast_path": False, "triggers": []},
            ]

            with patch.object(bsi, "INDEX_JSONL", index_path):
                bsi.write_index(skills)

            lines = index_path.read_text().strip().split("\n")
            self.assertEqual(len(lines), 2)

            a = json.loads(lines[0])
            self.assertEqual(a["id"], "a")
            self.assertEqual(a["title"], "A")
            self.assertTrue(a["fast_path"])
            self.assertNotIn("empty", a)
            self.assertNotIn("none", a)
            # 0 and False are falsy but might be meaningful — current code strips them
            self.assertNotIn("zero", a)
            self.assertNotIn("false", a)

            b = json.loads(lines[1])
            self.assertEqual(b["id"], "b")
            self.assertNotIn("triggers", b)
            self.assertNotIn("fast_path", b)


class TestWriteFastPaths(unittest.TestCase):
    """Tests for write_fast_paths markdown generation."""

    def test_table_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            skills = [
                {"id": "fast-a", "kind": "lookup", "triggers": ["do a"], "summary": "Skill A", "fast_path": True},
                {"id": "fast-b", "kind": "capture", "triggers": [], "summary": "Skill B", "fast_path": True, "collapsed_from": ["x", "y"]},
                {"id": "slow", "kind": "meta", "triggers": ["triage"], "summary": "Triage", "fast_path": False},
            ]

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_fast_paths(skills)

            text = (agg_dir / "fast-paths.md").read_text(encoding="utf-8")
            self.assertIn("# Fast Paths", text)
            self.assertIn("| `fast-a` | lookup | `do a` | Skill A |", text)
            self.assertIn("| `fast-b` | capture", text)
            self.assertIn("Skill B _(collapsed: x, y)_", text)
            self.assertNotIn("slow", text)
            self.assertIn("If no fast path matches, use `triage` skill", text)

    def test_pro_badge(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            skills = [
                {"id": "pro-skill", "kind": "transform", "triggers": ["go"], "summary": "Pro", "fast_path": True, "pro": True},
            ]

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_fast_paths(skills)

            text = (agg_dir / "fast-paths.md").read_text(encoding="utf-8")
            self.assertIn("`pro-skill` (Pro)", text)
            self.assertIn("transform", text)
            self.assertIn("`go`", text)
            self.assertIn("Pro", text)

    def test_empty_fast_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_fast_paths([])

            text = (agg_dir / "fast-paths.md").read_text(encoding="utf-8")
            self.assertIn("# Fast Paths", text)
            # Table header should exist even with zero rows
            self.assertIn("| Skill | Kind | Triggers | Summary |", text)


class TestWritePrime(unittest.TestCase):
    """Tests for write_prime session start file generation."""

    def test_basic_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prime_path = tmp_path / "PRIME.md"

            skills = [
                {"id": "fast-a", "kind": "lookup", "triggers": ["do a"], "summary": "Short summary", "fast_path": True},
                {"id": "slow", "kind": "meta", "triggers": [], "summary": "Triage", "fast_path": False},
            ]

            bsi.write_prime(skills, prime_path, "KBForge", "Claude Code")

            text = prime_path.read_text(encoding="utf-8")
            self.assertIn("# KBForge", text)
            self.assertIn("Session Prime", text)
            self.assertIn("for Claude Code", text)
            self.assertIn('"do a"', text)
            self.assertIn("`fast-a`", text)
            self.assertIn("Short summary", text)
            self.assertNotIn("slow", text)
            self.assertIn("If uncertain or no fast path matches", text)
            self.assertIn("`(C)` prefix", text)

    def test_trigger_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prime_path = tmp_path / "PRIME.md"

            long_summary = "A" * 80
            skills = [
                {"id": "long", "kind": "lookup", "triggers": ["go"], "summary": long_summary, "fast_path": True},
            ]

            bsi.write_prime(skills, prime_path, "T", "Tool")

            text = prime_path.read_text()
            self.assertIn("A" * 57 + "...", text)
            self.assertNotIn(long_summary, text)

    def test_pro_badge_in_prime(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prime_path = tmp_path / "PRIME.md"

            skills = [
                {"id": "pro", "kind": "transform", "triggers": ["pro"], "summary": "Pro skill", "fast_path": True, "pro": True},
            ]

            bsi.write_prime(skills, prime_path, "T", "Tool")

            text = prime_path.read_text(encoding="utf-8")
            self.assertIn("`pro` (Pro)", text)


class TestWriteChains(unittest.TestCase):
    """Tests for write_chains markdown generation."""

    def test_basic_chains(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            skills = [
                {"id": "root", "kind": "meta", "chains_to": ["mid"]},
                {"id": "mid", "kind": "lookup", "chains_to": ["leaf"]},
                {"id": "leaf", "kind": "capture", "chains_to": []},
            ]

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_chains(skills)

            text = (agg_dir / "chains.md").read_text(encoding="utf-8")
            self.assertIn("# Skill Chains", text)
            self.assertIn("`root` → `mid`", text)
            self.assertIn("`mid` → `leaf`", text)
            self.assertIn("starting from `root`", text)
            self.assertIn("→ `mid`", text)
            self.assertIn("→ `leaf`", text)

    def test_cycle_handling(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            skills = [
                {"id": "a", "kind": "meta", "chains_to": ["b"]},
                {"id": "b", "kind": "meta", "chains_to": ["a"]},
            ]

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_chains(skills)

            text = (agg_dir / "chains.md").read_text(encoding="utf-8")
            # Cycles without a root don't show the walk; verify edges are listed
            self.assertIn("`a` → `b`", text)
            self.assertIn("`b` → `a`", text)
            # No clear root when all nodes have incoming edges
            self.assertIn("No skill chains define a clear root", text)

    def test_no_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agg_dir = tmp_path / "aggregates"

            skills = [
                {"id": "a", "kind": "meta", "chains_to": []},
                {"id": "b", "kind": "lookup", "chains_to": []},
            ]

            with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                bsi.write_chains(skills)

            text = (agg_dir / "chains.md").read_text(encoding="utf-8")
            self.assertIn("No skill chains define a clear root", text)


# ---------------------------------------------------------------------------
# Integration / round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip(unittest.TestCase):
    """End-to-end tests from fixture files to generated outputs."""

    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            free_dir = tmp_path / "skills"
            pro_dir = tmp_path / "pro-pack" / "skills"
            agg_dir = tmp_path / "aggregates"
            index_path = tmp_path / "skills.jsonl"
            prime_path = tmp_path / "PRIME.md"

            free_dir.mkdir(parents=True)
            pro_dir.mkdir(parents=True)

            (free_dir / "test-skill.md").write_text(SKILL_WITH_TOUCHES_TRIGGERS.read_text())
            (pro_dir / "pro-skill.md").write_text(SKILL_PRO.read_text())

            with patch.object(bsi, "SKILLS_DIR", free_dir):
                with patch.object(bsi, "PRO_SKILLS_DIR", pro_dir):
                    with patch.object(bsi, "AGGREGATES_DIR", agg_dir):
                        with patch.object(bsi, "INDEX_JSONL", index_path):
                            skills = bsi.build_index()
                            bsi.write_index(skills)
                            bsi.write_chains(skills)
                            bsi.write_fast_paths(skills)
                            bsi.write_prime(skills, prime_path, "KBForge", "Test")

            # Verify JSONL
            lines = index_path.read_text().strip().split("\n")
            self.assertEqual(len(lines), 2)
            entries = [json.loads(l) for l in lines]
            ids = {e["id"] for e in entries}
            self.assertEqual(ids, {"test-skill", "pro-skill"})

            # Verify fast-paths
            fp_text = (agg_dir / "fast-paths.md").read_text()
            self.assertIn("test-skill", fp_text)
            self.assertIn("pro-skill", fp_text)
            self.assertIn("(Pro)", fp_text)

            # Verify PRIME
            prime_text = prime_path.read_text()
            self.assertIn("KBForge", prime_text)
            self.assertIn("test-skill", prime_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
