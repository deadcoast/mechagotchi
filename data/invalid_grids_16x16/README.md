# 16×16 Invalid Counterexample Corpus

Two hundred structurally invalid grids at the ratified default scale
(DR 0029; cycle 09 A2): the same four invalidators the 8×8 corpus uses
(duplicate coordinate, out-of-bounds cell, missing animation anchor,
organ reference to a missing cell) applied to each of the fifty 16×16
seeds. Every grid is rejected by the validator, pinned by
`labs/grid_genome/test_corpus_builder.py` (`Corpus16Tests`).
