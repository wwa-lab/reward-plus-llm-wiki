"""校验器回归测试：只在临时目录构造合成数据，不读取业务材料。"""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import validate_repo as validator


class ValidatorRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="wiki-validator-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in validator.REQUIRED_DIRS:
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        for filename in validator.REQUIRED_FILES:
            path = self.root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Synthetic fixture\n", encoding="utf-8")
        for filename in validator.REGISTRY_PREFIX:
            self.write_registry(filename, 0, [])
        for path in (self.root / "docs").glob("*.md"):
            path.write_text(self.front_matter("NEEDS_REVIEW", ""), encoding="utf-8")
        self.page = self.root / "knowledge/functions/FUNC-0001-synthetic.md"
        self.write_registry("functions.md", 1, ["FUNC-0001"])
        self.write_page("source_refs: []", status="NEEDS_REVIEW")

    @staticmethod
    def front_matter(status, evidence):
        return (
            "---\nid: FUNC-0001\ntitle: Synthetic fixture\nartifact_type: function\n"
            f"status: {status}\ncreated_at: 2026-10-12\nupdated_at: 2026-10-12\n"
            f"{evidence}\n---\n"
        )

    def write_page(self, evidence, status="EVIDENCE_FOUND"):
        self.page.write_text(self.front_matter(status, evidence), encoding="utf-8")

    def write_registry(self, filename, maximum, ids):
        text = f"当前最大 ID：{maximum}\n\n| ID | 名称 |\n|---|---|\n"
        text += "".join(f"| {fid} | Synthetic |\n" for fid in ids)
        (self.root / "knowledge/registry" / filename).write_text(text, encoding="utf-8")

    def evidence_report(self):
        report = validator.Report()
        validator.check_evidence_refs(self.root, report)
        return report

    def run_cli(self):
        output = io.StringIO()
        with patch("sys.argv", ["validate_repo.py", "--root", str(self.root)]):
            with contextlib.redirect_stdout(output):
                code = validator.main()
        return code, output.getvalue()

    def test_duplicate_registry_id_reports_both_rows_and_fails_cli(self):
        self.write_registry("functions.md", 1, ["FUNC-0001", "FUNC-0001"])
        code, output = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("ID 重复 'FUNC-0001'", output)
        self.assertIn("第5行、第6行", output)

    def test_unique_registry_ids_and_relation_mentions_are_allowed(self):
        self.write_registry("functions.md", 2, ["FUNC-0001", "FUNC-0002"])
        path = self.root / "knowledge/registry/functions.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("说明文字 FUNC-0001\n| — | FUNC-0001 |\n")
        report = validator.Report()
        ids = validator.check_registries(self.root, report)
        self.assertEqual(report.errors, [])
        self.assertEqual(ids["FUNC"], {"FUNC-0001", "FUNC-0002"})

    def test_missing_or_empty_evidence_fails_cli(self):
        for evidence in ("", "source_refs: []", "source_refs:", "source_refs: # pending"):
            with self.subTest(evidence=evidence):
                self.write_page(evidence)
                code, output = self.run_cli()
                self.assertEqual(code, 1)
                self.assertIn("至少一个非空路径", output)

    def test_empty_evidence_is_allowed_for_unreviewed_page(self):
        code, output = self.run_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("0 条警告", output)

    def test_unsupported_evidence_formats_fail_cli(self):
        invalid = (
            "source_refs:\n  - path: raw/PRJ-0001/business-documents/missing.md",
            "source_refs: [{path: raw/PRJ-0001/business-documents/missing.md}]",
            "source_refs: raw/PRJ-0001/business-documents/missing.md",
            "source_refs:\n  path: raw/PRJ-0001/business-documents/missing.md",
            "source_refs: null",
            "source_refs: [null]",
            "source_refs: [42]",
            'source_refs: [""]',
            "source_refs: ['   ']",
            "source_refs:\n  - raw/example.md\n    location: 1",
            "source_refs:\n  - raw/example.md\n    - raw/nested.md",
            "source_refs: []\nsource_refs: []",
            "source_refs: [raw/example.md,,raw/other.md]",
        )
        for evidence in invalid:
            with self.subTest(evidence=evidence):
                self.write_page(evidence, status="NEEDS_REVIEW")
                code, output = self.run_cli()
                self.assertEqual(code, 1, output)
                self.assertIn("source_refs", output)

    def test_supported_lists_check_missing_local_paths(self):
        ref = "raw/PRJ-0001/business-documents/missing.md"
        for evidence in (
            f"source_refs: [{ref}]",
            f'source_refs: ["{ref}"] # comment',
            f"source_refs:\n  # comment\n  - '{ref}' # comment",
            f"source_refs:\n- {ref}",
        ):
            with self.subTest(evidence=evidence):
                self.write_page(evidence)
                report = self.evidence_report()
                self.assertEqual(report.errors, [])
                self.assertEqual(len(report.warnings), 1)
                self.assertIn(ref, report.warnings[0])

    def test_existing_evidence_passes_cli_with_quotes_and_punctuation(self):
        ref = "tests/validation/synthetic, # example.txt"
        (self.root / ref).write_text("Synthetic evidence", encoding="utf-8")
        for evidence in (
            f'source_refs: ["{ref}"]',
            f"source_refs:\n  - '{ref}' # comment",
        ):
            with self.subTest(evidence=evidence):
                self.write_page(evidence)
                code, output = self.run_cli()
                self.assertEqual(code, 0, output)
                self.assertIn("0 条警告", output)

    def test_lan_paths_and_configuration_exemption_are_preserved(self):
        self.write_page(
            "source_refs:\n"
            "  - //synthetic-server/share/source.txt\n"
            "  - raw/PRJ-0001/control-files/synthetic.txt"
        )
        report = self.evidence_report()
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])
        self.assertEqual(len(report.info), 1)


if __name__ == "__main__":
    unittest.main()
