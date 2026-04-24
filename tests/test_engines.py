"""
Djinn engine sanity tests — stdlib only.
Run: python -m unittest tests.test_engines -v
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "shared" / "scripts"))

from engines.c1_lcs import normalize, preservation_ratio
from engines.c2_hmm import infer_states, STATES
from engines.c3_reservoir import update_reservoir
from engines.c4_pagerank import pagerank
from engines.c5_gauss import update_posterior
from bootstrap_ci import bootstrap_ci


class TestD1LCS(unittest.TestCase):
    def test_normalize_drops_stopwords(self):
        self.assertEqual(normalize("The Quick Brown Fox"), ["quick", "brown", "fox"])

    def test_identical_inputs_yield_1(self):
        toks = normalize("add dark mode toggle to settings")
        self.assertEqual(preservation_ratio(toks, toks), 1.0)

    def test_disjoint_inputs_yield_0(self):
        a = normalize("add dark mode toggle")
        b = normalize("refactor database migration schema")
        self.assertLess(preservation_ratio(a, b), 0.3)

    def test_empty_anchor_returns_1(self):
        self.assertEqual(preservation_ratio([], ["anything"]), 1.0)


class TestD2HMM(unittest.TestCase):
    def test_empty_observations_returns_empty(self):
        self.assertEqual(infer_states([]), [])

    def test_output_length_matches_input(self):
        obs = [("Read", "on_task"), ("Edit", "on_task"), ("Bash", "sidequest")]
        states = infer_states(obs)
        self.assertEqual(len(states), len(obs))
        for s in states:
            self.assertIn(s, STATES)


class TestD3Reservoir(unittest.TestCase):
    def test_under_k_appends(self):
        r = update_reservoir([], {"turn": 1, "score": 0.9}, n_seen=1, k=32)
        self.assertEqual(len(r), 1)

    def test_at_capacity_stays_capacity(self):
        r = [{"turn": i, "score": 0.5} for i in range(32)]
        for i in range(33, 100):
            r = update_reservoir(r, {"turn": i, "score": 0.5}, n_seen=i, k=32)
        self.assertEqual(len(r), 32)


class TestD4PageRank(unittest.TestCase):
    def test_empty_graph(self):
        self.assertEqual(pagerank({}), {})

    def test_scores_sum_to_one(self):
        dag = {"a": ["b", "c"], "b": ["c"], "c": []}
        pr = pagerank(dag)
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=3)
        self.assertGreater(pr["c"], pr["a"])  # c has two in-edges

    def test_dangling_node_survives(self):
        dag = {"a": ["b"], "b": []}
        pr = pagerank(dag)
        self.assertIn("b", pr)
        self.assertIn("a", pr)


class TestD5Gauss(unittest.TestCase):
    def test_first_observation_seeds_posterior(self):
        p = update_posterior({}, {"preservation_score": 0.8, "session_length": 40})
        self.assertEqual(p["n_sessions"], 1)
        self.assertAlmostEqual(p["median_preservation"], 0.8, places=4)

    def test_repeated_same_obs_converges(self):
        p = {}
        for _ in range(20):
            p = update_posterior(p, {"preservation_score": 0.9, "session_length": 30})
        self.assertAlmostEqual(p["median_preservation"], 0.9, places=2)
        self.assertLess(p["sigma"], 0.05)
        self.assertEqual(p["n_sessions"], 20)


class TestBootstrapCI(unittest.TestCase):
    def test_empty_returns_zeros(self):
        self.assertEqual(bootstrap_ci([]), (0.0, 0.0, 0.0, 0))

    def test_single_sample_collapses_band(self):
        v, lo, hi, n = bootstrap_ci([0.7])
        self.assertEqual((v, lo, hi, n), (0.7, 0.7, 0.7, 1))

    def test_multi_sample_band_ordering(self):
        v, lo, hi, n = bootstrap_ci([0.5, 0.6, 0.7, 0.8, 0.9, 0.55, 0.65, 0.75])
        self.assertLessEqual(lo, v)
        self.assertLessEqual(v, hi)
        self.assertEqual(n, 8)


if __name__ == "__main__":
    unittest.main()
