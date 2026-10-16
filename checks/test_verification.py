import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.verification import (check_inputs,check_numeric,source_hashes,check_freshness,
                                 complete_run,required_outputs)
from shared.scoring import check_split_identity
from checks.check_outputs import check_code_link


class VerificationTests(unittest.TestCase):
    def test_all_frozen_inputs(self):
        self.assertEqual(check_inputs(ROOT),7)

    def test_input_mutation_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'data').mkdir()
            (root/'data/x.csv').write_text('changed')
            (root/'data/input-checksums.csv').write_text('path,md5\ndata/x.csv,'+hashlib.md5(b'original').hexdigest())
            with self.assertRaisesRegex(ValueError,'checksum mismatch'): check_inputs(root)

    def test_split_reordering_fails(self):
        original=ROOT/'data/credit-scoring/reference-split.csv'
        check_split_identity(original)
        with tempfile.TemporaryDirectory() as directory:
            changed=Path(directory)/'split.csv'
            lines=original.read_bytes().splitlines(keepends=True)
            lines[1],lines[2]=lines[2],lines[1]
            changed.write_bytes(b''.join(lines))
            with self.assertRaisesRegex(ValueError,'split checksum'): check_split_identity(changed)

    def test_numeric_mutation_fails(self):
        cases=[dict(path=['price'],expected=[94/1.05],atol=1e-10,rtol=1e-10)]
        self.assertEqual(check_numeric({'price':94/1.05},cases),1)
        with self.assertRaisesRegex(ValueError,'Numeric reference'): check_numeric({'price':90},cases)


class OutputFreshnessTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for folder in ('chapters','shared','data'):
            (self.root/folder).mkdir()
        for name in ('run.py','_quarto.yml','chapters.json','requirements-lock.txt','data/input-checksums.csv'):
            (self.root/name).write_text('reference')
        (self.root/'results-index.csv').write_text(
            'chapter,output\nexample,output/example/tables/table-1-1.csv\n'
            'example,output/example/figures/figure-1-1.png\n')
        self.paths = required_outputs(self.root, 'example')
        for path in self.paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original output')
        self.started = time.time()-1
        self.before = source_hashes(self.root)
        self.manifest = self.root/'output/example/run-manifest.json'
        complete_run(self.root, 'example', self.started, self.before)

    def test_complete_run_records_every_output(self):
        check_freshness(self.root, 'example')
        recorded = json.loads(self.manifest.read_text())
        self.assertEqual(len(recorded['outputs']), 4)
        for path in self.paths:
            entry = recorded['outputs'][path.relative_to(self.root).as_posix()]
            self.assertEqual(entry['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(entry['mtime_ns'], path.stat().st_mtime_ns)

    def test_updated_input_manifest_requires_rerun(self):
        (self.root/'data/input-checksums.csv').write_text('new approved checksums')
        with self.assertRaisesRegex(ValueError,'source files changed'):
            check_freshness(self.root,'example')

    def test_changed_output_fails_even_with_original_mtime(self):
        for path in self.paths:
            with self.subTest(path=path.name):
                original, stamp = path.read_bytes(), path.stat().st_mtime_ns
                path.write_bytes(b'mutated output')
                os.utime(path, ns=(stamp, stamp))
                with self.assertRaisesRegex(ValueError, 'output changed or missing'):
                    check_freshness(self.root, 'example')
                path.write_bytes(original)
                os.utime(path, ns=(stamp, stamp))

    def test_changed_mtime_fails_even_with_original_bytes(self):
        path = self.paths[0]
        stamp = path.stat().st_mtime_ns+10_000_000_000
        os.utime(path, ns=(stamp, stamp))
        with self.assertRaisesRegex(ValueError, 'output changed or missing'):
            check_freshness(self.root, 'example')

    def test_deleted_output_fails(self):
        self.paths[0].unlink()
        with self.assertRaisesRegex(ValueError, 'output changed or missing'):
            check_freshness(self.root, 'example')

    def test_incomplete_and_legacy_manifests_fail(self):
        recorded = json.loads(self.manifest.read_text())
        del recorded['outputs'][self.paths[0].relative_to(self.root).as_posix()]
        self.manifest.write_text(json.dumps(recorded))
        with self.assertRaisesRegex(ValueError, 'output fingerprints'):
            check_freshness(self.root, 'example')
        del recorded['outputs']
        self.manifest.write_text(json.dumps(recorded))
        with self.assertRaisesRegex(ValueError, 'output fingerprints'):
            check_freshness(self.root, 'example')

    def test_stale_source_fails(self):
        (self.root/'run.py').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source files changed'):
            check_freshness(self.root, 'example')

    def test_incomplete_render_does_not_issue_manifest(self):
        self.manifest.unlink()
        path = self.paths[0]
        os.utime(path, (self.started-60, self.started-60))
        with self.assertRaisesRegex(RuntimeError, 'Missing or stale output'):
            complete_run(self.root, 'example', self.started, self.before)
        self.assertFalse(self.manifest.exists())
        path.unlink()
        with self.assertRaisesRegex(RuntimeError, 'Missing or stale output'):
            complete_run(self.root, 'example', self.started, self.before)
        self.assertFalse(self.manifest.exists())

    def test_sources_changed_during_render_fail(self):
        self.manifest.unlink()
        (self.root/'run.py').write_text('changed')
        with self.assertRaisesRegex(RuntimeError, 'Sources changed during rendering'):
            complete_run(self.root, 'example', self.started, self.before)
        self.assertFalse(self.manifest.exists())

    def test_foundations_requires_fresh_unnumbered_figures(self):
        paths = required_outputs(self.root, '00-foundations')
        self.assertEqual(len(paths), 4)
        for path in paths[:2]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'fresh output')
        with self.assertRaisesRegex(RuntimeError, 'figure-foundations-loss'):
            complete_run(self.root, '00-foundations', self.started, self.before)
        for path in paths[2:]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'figure')
        os.utime(paths[-1], (self.started-60, self.started-60))
        with self.assertRaisesRegex(RuntimeError, 'figure-foundations-normal'):
            complete_run(self.root, '00-foundations', self.started, self.before)
        os.utime(paths[-1], None)
        self.assertEqual(complete_run(self.root, '00-foundations', self.started, self.before), 4)
        check_freshness(self.root, '00-foundations')
        paths[-1].write_bytes(b'changed figure')
        with self.assertRaisesRegex(ValueError, 'output changed or missing'):
            check_freshness(self.root, '00-foundations')


class CodeLinkTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.folder = self.root/'chapters/example'
        self.folder.mkdir(parents=True)
        self.source = self.folder/'chapter.qmd'
        self.source.write_text(
            '### Table 1.1 {#result-table-1-1}\n```{python}\n'
            "show_table(out, '1.1', first)\n```\n"
            '### Table 1.2 {#result-table-1-2}\n```{python}\n'
            "show_table(out, '1.2', second)\n```\n")
        self.readme = self.folder/'README.md'
        self.readme.write_text(
            '| Table 1.1 | First | [Code](chapter.qmd#L2) |\n'
            '| Table 1.2 | Second | [Code](chapter.qmd#L6) |\n')
        self.row = dict(chapter='example', source='chapters/example/chapter.qmd',
                        kind='Table', number='1.1', anchor='result-table-1-1', source_line='2')

    def test_all_current_indexed_chunks(self):
        with (ROOT/'results-index.csv').open(encoding='utf-8-sig') as handle:
            for row in csv.DictReader(handle):
                with self.subTest(result=row['book_id']):
                    check_code_link(ROOT, row)

    def test_correct_link_passes_and_other_fence_fails(self):
        check_code_link(self.root, self.row)
        self.row['source_line'] = '6'
        with self.assertRaisesRegex(ValueError, 'wrong result heading'):
            check_code_link(self.root, self.row)

    def test_wrong_emitted_result_fails(self):
        self.source.write_text(self.source.read_text().replace("'1.1'", "'1.2'"))
        with self.assertRaisesRegex(ValueError, 'does not emit'):
            check_code_link(self.root, self.row)

    def test_swapped_readme_links_fail(self):
        self.readme.write_text(
            '| Table 1.1 | First | [Code](chapter.qmd#L6) |\n'
            '| Table 1.2 | Second | [Code](chapter.qmd#L2) |\n')
        with self.assertRaisesRegex(ValueError, 'README code link'):
            check_code_link(self.root, self.row)


if __name__=='__main__': unittest.main()
