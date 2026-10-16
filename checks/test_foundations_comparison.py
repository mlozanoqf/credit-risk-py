"""Schema and statistical regression checks without private R reference files."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from checks.compare_scoring import compare_foundations, FOUNDATIONS_KEYS


class FoundationsComparisonTests(unittest.TestCase):
    def setUp(self):
        # Synthetic shared values exercise every deterministic key; simulation
        # summaries are the saved 10,000-scenario Python and R baselines.
        self.python = dict.fromkeys(FOUNDATIONS_KEYS, 1.0)
        self.python['new_applicant_pd'] = [.04, .12, .12]
        self.python['loan_el'] = [8., 48., 200.]
        self.reference = deepcopy(self.python)
        self.python.update(simulated_mean_loss=[996.5, 1013.],
                           simulated_joint_pd=[.0104, .1013])
        self.reference.update(n_scenarios=10000, simulation_check=[
            dict(exact_mean_loss=1000., simulated_mean_loss=1047.,
                 exact_joint_pd=.01, simulated_joint_pd=.0101),
            dict(exact_mean_loss=1000., simulated_mean_loss=1069.,
                 exact_joint_pd=.1, simulated_joint_pd=.1069)])

    def test_nested_r_baseline_and_diagnostics(self):
        exact, mc = compare_foundations(self.python, self.reference)
        self.assertEqual(len(exact), 56)
        self.assertEqual(len(mc), 12)
        self.assertTrue(all(row['Tolerance met'] for row in exact+mc))
        self.assertAlmostEqual(max(abs(row['Signed standard errors']) for row in mc), 2.3)
        expected_se = [np.sqrt(450), 30., np.sqrt(.01*.99/10000), .003]
        for metric, errors in zip(('simulated_mean_loss', 'simulated_joint_pd'),
                                  (expected_se[:2], expected_se[2:])):
            rows = [row for row in mc if row['Comparison'].endswith(metric)]
            np.testing.assert_allclose([row['Standard error'] for row in rows],
                                       errors+errors+list(np.sqrt(2)*np.array(errors)))
        for row in mc:
            self.assertEqual(row['Scenarios per run'], 10000)
            self.assertEqual(row['SE limit'], 4.)
            self.assertAlmostEqual(row['Absolute tolerance'], 4*row['Standard error'])

    def test_all_deterministic_keys_reject_mutation(self):
        for key in FOUNDATIONS_KEYS:
            with self.subTest(key=key):
                changed = deepcopy(self.python)
                changed[key] = np.asarray(changed[key])+1
                with self.assertRaisesRegex(AssertionError, key):
                    compare_foundations(changed, self.reference)

    def test_deterministic_tolerance(self):
        self.python['total_exposure'] += 1e-12
        compare_foundations(self.python, self.reference)
        self.python['total_exposure'] += 1e-10
        with self.assertRaisesRegex(AssertionError, 'total_exposure'):
            compare_foundations(self.python, self.reference)

    def test_missing_or_unexpected_deterministic_keys(self):
        for source in ('python', 'reference'):
            with self.subTest(source=source):
                py, rr = deepcopy(self.python), deepcopy(self.reference)
                del (py if source == 'python' else rr)['bond_q']
                with self.assertRaisesRegex(AssertionError, 'bond_q'):
                    compare_foundations(py, rr)
        self.python['unreviewed_result'] = 1
        with self.assertRaisesRegex(AssertionError, 'unreviewed_result'):
            compare_foundations(self.python, self.reference)

    def test_every_simulation_summary_rejects_large_mutation(self):
        for source in ('Python', 'R'):
            for key, bad in (('simulated_mean_loss', 2000.), ('simulated_joint_pd', .5)):
                for i in range(2):
                    with self.subTest(source=source, key=key, portfolio=i):
                        py, rr = deepcopy(self.python), deepcopy(self.reference)
                        if source == 'Python':
                            py[key][i] = bad
                        else:
                            rr['simulation_check'][i][key] = bad
                        with self.assertRaisesRegex(AssertionError, source+' vs analytical'):
                            compare_foundations(py, rr)

    def test_agreement_between_wrong_runs_is_not_sufficient(self):
        self.python['simulated_mean_loss'][0] = 2000.
        self.reference['simulation_check'][0]['simulated_mean_loss'] = 2000.
        with self.assertRaisesRegex(AssertionError, 'Python vs analytical'):
            compare_foundations(self.python, self.reference)

    def test_four_se_limit(self):
        self.python['simulated_mean_loss'][1] = 1000+3.9*30
        compare_foundations(self.python, self.reference)
        self.python['simulated_mean_loss'][1] = 1000+4.1*30
        with self.assertRaisesRegex(AssertionError, 'perfectly joint: simulated_mean_loss'):
            compare_foundations(self.python, self.reference)

    def test_cross_run_difference_uses_combined_uncertainty(self):
        self.python['simulated_mean_loss'][1] = 1000+3*30
        self.reference['simulation_check'][1]['simulated_mean_loss'] = 1000-3*30
        with self.assertRaisesRegex(AssertionError, 'Python minus R'):
            compare_foundations(self.python, self.reference)

    def test_nonfinite_values_fail_even_when_both_match(self):
        for value in (float('nan'), float('inf')):
            for key in ('bond_q', 'simulated_mean_loss', 'simulated_joint_pd'):
                with self.subTest(value=value, key=key):
                    py, rr = deepcopy(self.python), deepcopy(self.reference)
                    if key == 'bond_q':
                        py[key] = rr[key] = value
                    else:
                        py[key][0] = rr['simulation_check'][0][key] = value
                    with self.assertRaisesRegex(AssertionError, 'finite'):
                        compare_foundations(py, rr)

    def test_shapes_and_missing_simulation_fields_fail(self):
        for key in ('loan_el', 'simulated_mean_loss', 'simulated_joint_pd'):
            with self.subTest(key=key):
                py = deepcopy(self.python)
                py[key] = [py[key]]
                with self.assertRaisesRegex(AssertionError, 'shape'):
                    compare_foundations(py, self.reference)
        for records in ({}, self.reference['simulation_check'][:1], [{}, {}]):
            rr = deepcopy(self.reference)
            rr['simulation_check'] = records
            with self.assertRaisesRegex(AssertionError, 'two complete records'):
                compare_foundations(self.python, rr)
        del self.python['simulated_joint_pd']
        with self.assertRaisesRegex(AssertionError, 'simulated_joint_pd'):
            compare_foundations(self.python, self.reference)

    def test_simulation_design_and_record_order_are_checked(self):
        self.reference['n_scenarios'] = 1000
        with self.assertRaisesRegex(AssertionError, 'n_scenarios=10000'):
            compare_foundations(self.python, self.reference)
        self.reference['n_scenarios'] = 10000
        self.reference['simulation_check'].reverse()
        with self.assertRaisesRegex(AssertionError, 'analytical targets'):
            compare_foundations(self.python, self.reference)


if __name__ == '__main__':
    unittest.main()
