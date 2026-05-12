import unittest

from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from lineage_tracker import build_lineage_graph, summarize_lineage_graph


class LineageTrackerTests(unittest.TestCase):
    def test_constrained_children_record_seed_parent(self):
        children = build_constrained_corpus(build_seed_grids(), count=10, rng_seed=909)

        for child in children:
            with self.subTest(grid_id=child["grid_id"]):
                self.assertIsNotNone(child["parent_grid_id"])
                self.assertEqual(1, child["lineage"]["generation"])
                self.assertIn(child["parent_grid_id"], child["lineage"]["ancestor_ids"])

    def test_lineage_graph_contains_seed_and_child_nodes(self):
        seeds = build_seed_grids()
        children = build_constrained_corpus(seeds, count=25, rng_seed=909)

        graph = build_lineage_graph(seeds, children)

        self.assertEqual(75, len(graph["nodes"]))
        self.assertEqual(25, len(graph["edges"]))
        self.assertEqual(0, len(graph["orphans"]))

    def test_lineage_summary_reports_depth_and_dominance(self):
        seeds = build_seed_grids()
        children = build_constrained_corpus(seeds, count=25, rng_seed=909)
        graph = build_lineage_graph(seeds, children)

        summary = summarize_lineage_graph(graph)

        self.assertEqual(75, summary["node_count"])
        self.assertEqual(25, summary["edge_count"])
        self.assertEqual(1, summary["max_generation"])
        self.assertGreater(summary["dominant_lineage_share"], 0)


if __name__ == "__main__":
    unittest.main()
