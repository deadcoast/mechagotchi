import argparse
import json
from copy import deepcopy
from pathlib import Path

# PALETTES and _cell are re-exported here for backward compatibility:
# markov_grid, constrained_generator, and cross-lab consumers
# (workshop_editor, cellular_automata) import them from corpus_builder.
from grid_helpers import PALETTES, _cell, grid_from_matrix, grid_from_rich_matrix


ROOT = Path(__file__).resolve().parents[2]


BLUEPRINTS = [
    ("mg_seed_001", "lcd_green", [".E..E...", "..BB....", ".BABB...", "..BB.M..", "...BB...", "........", "........", "........"]),
    ("mg_seed_002", "gameboy_gray", ["........", "..E.E...", "..BBB...", ".BBABB..", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_003", "amber_terminal", ["........", "...E....", "..BBB...", ".BBABB..", "..BMB...", "...E....", "........", "........"]),
    ("mg_seed_004", "crt_blue", ["..E..E..", "...B....", "..BAB...", ".BBBB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_005", "pocket_plum", ["........", "..E..E..", ".BBBB...", ".BABBB..", "..BMB...", "..BBB...", "........", "........"]),
    ("mg_seed_006", "lcd_green", ["........", "...E....", "..BBB...", "..BAB...", "..BBB...", ".E.M.E..", "........", "........"]),
    ("mg_seed_007", "gameboy_gray", ["........", ".E....E.", "..BBBB..", "..BABB..", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_008", "amber_terminal", ["........", "..E.E...", ".BBBB...", "...AB...", ".BBBB...", "...M....", "........", "........"]),
    ("mg_seed_009", "crt_blue", ["........", "...E.E..", "..BBBB..", ".BBAB...", "..BMB...", "..B.....", "........", "........"]),
    ("mg_seed_010", "pocket_plum", ["........", ".E.E....", "..BBB...", "..BABB..", "..BMB...", "....B...", "........", "........"]),
    ("mg_seed_011", "lcd_green", ["........", "...E....", ".BBBB...", "..BAB...", ".BBBB...", "...M.E..", "........", "........"]),
    ("mg_seed_012", "gameboy_gray", ["........", "..E..E..", "...BB...", "..BABB..", "...BM...", "..BBB...", "........", "........"]),
    ("mg_seed_013", "amber_terminal", ["........", ".E..E...", ".BBBB...", ".BABB...", "..BM....", "..BB....", "........", "........"]),
    ("mg_seed_014", "crt_blue", ["........", "..E.....", "..BBB...", ".BBABB..", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_015", "pocket_plum", ["........", "....E...", "..BBBB..", "..BABB..", "..BMB...", "..E.....", "........", "........"]),
    ("mg_seed_016", "lcd_green", ["........", "..E.E...", "...BBB..", "..BABB..", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_017", "gameboy_gray", ["........", ".E...E..", "..BBBB..", ".BBAB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_018", "amber_terminal", ["........", "..E.....", ".BBBB...", ".BABBB..", "...BM...", ".....E..", "........", "........"]),
    ("mg_seed_019", "crt_blue", ["........", "...E.E..", "..BBB...", ".BABB...", ".BBM....", "..B.....", "........", "........"]),
    ("mg_seed_020", "pocket_plum", ["........", ".E..E...", "..BBB...", "..BABB..", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_021", "lcd_green", ["........", "..E..E..", ".BBBB...", "..BABB..", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_022", "gameboy_gray", ["........", "...E....", "..BBBB..", ".BBABB..", "..BMB...", ".E......", "........", "........"]),
    ("mg_seed_023", "amber_terminal", ["........", ".E.E....", "..BBBB..", "..BABB..", "...BM...", "....B...", "........", "........"]),
    ("mg_seed_024", "crt_blue", ["........", "..E...E.", "...BBB..", "..BABB..", ".BBM....", "..BB....", "........", "........"]),
    ("mg_seed_025", "pocket_plum", ["........", "...E.E..", ".BBBB...", ".BABB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_026", "lcd_green", ["........", "..E.....", "..BBBB..", "..BABB..", ".BBM....", "....E...", "........", "........"]),
    ("mg_seed_027", "gameboy_gray", ["........", "...E.E..", "..BBBB..", ".BBAB...", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_028", "amber_terminal", ["........", ".E..E...", "...BBB..", "..BABB..", "..BMB...", "..BB....", "........", "........"]),
    ("mg_seed_029", "crt_blue", ["........", "..E.E...", ".BBBB...", "...AB...", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_030", "pocket_plum", ["........", "...E....", "..BBB...", ".BBABB..", ".BBM....", "....E...", "........", "........"]),
    ("mg_seed_031", "lcd_green", ["........", ".E...E..", "..BBBB..", "..BAB...", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_032", "gameboy_gray", ["........", "...E....", ".BBBB...", ".BABBB..", "..BM....", "..E.....", "........", "........"]),
    ("mg_seed_033", "amber_terminal", ["........", "..E..E..", "...BBB..", "..BABB..", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_034", "crt_blue", ["........", ".E.E....", ".BBBB...", ".BBAB...", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_035", "pocket_plum", ["........", "..E...E.", "..BBB...", "..BABB..", "..BMB...", "..B.....", "........", "........"]),
    ("mg_seed_036", "lcd_green", ["........", "...E.E..", ".BBBB...", "..BAB...", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_037", "gameboy_gray", ["........", "..E.....", "...BBB..", "..BABB..", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_038", "amber_terminal", ["........", ".E..E...", "..BBBB..", ".BBAB...", "..BM....", "...BB...", "........", "........"]),
    ("mg_seed_039", "crt_blue", ["........", "...E....", "..BBBB..", "..BABB..", "..BMB...", ".E......", "........", "........"]),
    ("mg_seed_040", "pocket_plum", ["........", "..E.E...", ".BBBB...", ".BAB....", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_041", "lcd_green", ["........", "..E..E..", "...BBB..", ".BBABB..", "..BM....", "...B....", "........", "........"]),
    ("mg_seed_042", "gameboy_gray", ["........", ".E...E..", ".BBBB...", "..BABB..", "...BM...", "...B....", "........", "........"]),
    ("mg_seed_043", "amber_terminal", ["........", "...E....", "..BBB...", ".BBAB...", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_044", "crt_blue", ["........", "..E.E...", ".BBBB...", "..BAB...", "..BMB...", "....B...", "........", "........"]),
    ("mg_seed_045", "pocket_plum", ["........", ".E..E...", "..BBBB..", "..BABB..", ".BBM....", "........", "........", "........"]),
    ("mg_seed_046", "lcd_green", ["........", "...E.E..", "..BBB...", ".BBABB..", "...BM...", "...B....", "........", "........"]),
    ("mg_seed_047", "gameboy_gray", ["........", "..E.....", ".BBBB...", ".BABB...", "..BMB...", "....E...", "........", "........"]),
    ("mg_seed_048", "amber_terminal", ["........", "...E....", "..BBBB..", "..BABB..", ".BBM....", ".....E..", "........", "........"]),
    ("mg_seed_049", "crt_blue", ["........", ".E.E....", "...BBB..", "..BABB..", "..BMB...", "..BB....", "........", "........"]),
    ("mg_seed_050", "pocket_plum", ["........", "..E..E..", ".BBBB...", ".BBAB...", "..BM....", "...BB...", "........", "........"]),
]


# The 16x16 seed corpus (cycle 09 A2, DR 0029): seeds 001-010 are the ten
# invariant-scaling pilot exemplars (imported lazily to avoid a module
# cycle); 011-050 are authored here. Rich-token alphabet (grid_helpers
# RICH_TOKENS, DR 0015 vocabulary), eight new creatures per palette, real
# morphological variety — NOT upscaled 8x8 blobs. Every seed carries a
# sensor pair (>=2 eyes) and a core of at least 18 cells (the ratified
# 16x16 floor), pinned by test_corpus_builder.
BLUEPRINTS_16 = [
    # -- lcd_green --------------------------------------------------------
    ("mg_seed16_011_mantis", "lcd_green", [
        "................",
        "....E......E....",
        ".....BBBBBB.....",
        "......BMMB......",
        "..L...BBBB...L..",
        "..LLLBBABBBLL...",
        "..LL..BBBB..LL..",
        ".......BB.......",
        "......BBBB......",
        "......BBBB......",
        "......BBBB......",
        ".......BB.......",
        "......J..J......",
        "......L..L......",
        "................",
        "................",
    ]),
    ("mg_seed16_012_snail", "lcd_green", [
        "................",
        "..E..E..........",
        "..N..N..........",
        "..N..N..SSSS....",
        ".MBBBB.SSSSSS...",
        "..BBBBSSDDSSS...",
        ".BBBBBSDSSDSS...",
        ".BABBBSSDDSSS...",
        ".BBBBBBSSSSS....",
        ".BBBBBBBBBB.....",
        "..BBBBBBBBBB....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_013_sprout", "lcd_green", [
        "................",
        ".......DD.......",
        "......NBBN......",
        ".......BB.......",
        "..DD..BBBB..DD..",
        "...DDBBBBBBDD...",
        ".....BBABBB.....",
        "....EBBBBBBE....",
        "....BBBBBBBB....",
        "....BBBMMBBB....",
        ".....BBBBBB.....",
        "......BBBB......",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_014_hopper", "lcd_green", [
        "................",
        "...EE......EE...",
        "...BB......BB...",
        "..BBBBBBBBBBBB..",
        "..BBBBBBBBBBBB..",
        "..BBBABBBBBBBB..",
        "...BMMMMMMMMB...",
        "..BBBBBBBBBBBB..",
        ".JBBBBBBBBBBBBJ.",
        ".LL.BBBBBBBB.LL.",
        ".LL..........LL.",
        "..LL........LL..",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_015_drone", "lcd_green", [
        "................",
        "....N......N....",
        "....P......P....",
        "...SSSSSSSSSS...",
        "...SBBBBBBBBS...",
        "...SBEEBBEEBS...",
        "...SBBBABBBBS...",
        "...SBBMMMMBBS...",
        "...SBBBBBBBBS...",
        "...SSSSSSSSSS...",
        "....F......F....",
        "....F......F....",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_016_lantern", "lcd_green", [
        ".......BB.......",
        ".......BB.......",
        "......BBBB......",
        ".....BBBBBB.....",
        "....BEEBBEEB....",
        "....BBBBBBBB....",
        "....BBBABBBB....",
        "....BBBMMBBB....",
        ".....BBBBBB.....",
        "......BBBB......",
        ".....D.DD.D.....",
        ".....D....D.....",
        "......F..F......",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_017_pupfish", "lcd_green", [
        "................",
        "................",
        ".....F..........",
        "....F...........",
        "..BBBBBBBBBB....",
        ".BBEBBBBBBBBL...",
        ".BBEBBBBBBBBLL..",
        ".MBBBBBABBBBL...",
        "..BBBBBBBBBB....",
        "...D...D........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_018_warden", "lcd_green", [
        "................",
        "......EBBE......",
        "......BMMB......",
        ".SS.BBBBBBBB....",
        ".SSBBBBBBBBB....",
        ".SSBBBABBBBB....",
        ".SSBBBBBBBBB....",
        ".SS.BBBBBBBB....",
        "....BBB..BBB....",
        "....BBB..BBB....",
        "....LLL..LLL....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # -- gameboy_gray -----------------------------------------------------
    ("mg_seed16_019_bat", "gameboy_gray", [
        "................",
        "...N........N...",
        "...NN......NN...",
        "....BEBBBBEB....",
        "....BBBABBBB....",
        "..LLBBMMMMBBLL..",
        ".LLLBBBBBBBBLLL.",
        "LLLL.BBBBBB.LLLL",
        "LLL...BBBB...LLL",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_020_scorpion", "gameboy_gray", [
        "................",
        "..LL........LL..",
        ".LLLL......LLLL.",
        ".LL..........LL.",
        "..J..........J..",
        "...BEBBBBBBEB...",
        "...BBBBABBBBB...",
        "....BBBBBBBB....",
        "....JBBBBBBJ....",
        "....J.BBBB.J....",
        ".......BB.......",
        ".......BB.......",
        ".......BB.......",
        "......DD........",
        "................",
        "................",
    ]),
    ("mg_seed16_021_hermit", "gameboy_gray", [
        "................",
        "..E..E..........",
        "..N..N..SSSSS...",
        ".BBBBB.SSDDSS...",
        ".BBBBBSSDSSDS...",
        ".BABBBSSDDSSS...",
        ".BBBBBBSSSSSS...",
        ".MBBBB.SSSSS....",
        "..JBBJ..........",
        ".LL..LL.........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_022_rat", "gameboy_gray", [
        "................",
        "..BB............",
        ".BBBB...........",
        ".BEEBB..........",
        "NBBBBBB.........",
        ".MBBBBBBBB......",
        "..BBABBBBBBB....",
        "..BBBBBBBBBB....",
        "...BBBBBBBB.L...",
        "...LL..LL..L....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_023_hornbeetle", "gameboy_gray", [
        ".......BB.......",
        ".......BB.......",
        "......BMMB......",
        "....EBBBBBBE....",
        "..SSBBBBBBBBSS..",
        ".SSBBBBBBBBBBSS.",
        ".SBBBBBABBBBBBS.",
        ".SBBBBBBBBBBBBS.",
        ".SSBBBBBBBBBBSS.",
        "..SSBBBBBBBBSS..",
        "...SSSSSSSSSS...",
        "..J..J....J..J..",
        "..L..L....L..L..",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_024_automaton", "gameboy_gray", [
        "................",
        ".....BBBBBB.....",
        ".....BEBBEB.....",
        ".....BMMMMB.....",
        "......BBBB......",
        "...BBBBBBBBBB...",
        "...BBBABBBBBBDD.",
        "...BBBBBBBBBB.D.",
        "...BBBBBBBBBB...",
        "....BBB..BBB....",
        "....BBB..BBB....",
        "....LLL..LLL....",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_025_spider", "gameboy_gray", [
        "................",
        ".L............L.",
        ".L.L........L.L.",
        "..L.L......L.L..",
        "...L.L....L.L...",
        "....LBBBBBBL....",
        "....BEBBBBEB....",
        "....BBBABBBB....",
        "....LBBBBBBL....",
        "...L.BBBBBB.L...",
        "..L...BBBB...L..",
        ".L............L.",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_026_mole", "gameboy_gray", [
        "................",
        "................",
        "....BBBBBB......",
        "..BBBBBBBBBB....",
        ".BEEBBBBBBBBB...",
        ".MBBBBBBABBBBB..",
        "LLBBBBBBBBBBBB..",
        "LL.BBBBBBBBBB...",
        "....BBBBBBBB....",
        "....LL....LL....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # -- amber_terminal ---------------------------------------------------
    ("mg_seed16_027_scarab", "amber_terminal", [
        ".......DD.......",
        "......DDDD......",
        ".......BB.......",
        "....EBBBBBBE....",
        "...LBBBBBBBBL...",
        "..LLBBBBBBBBLL..",
        "....BBBABBBB....",
        "...LBBBBBBBBL...",
        "..LL.BBBBBB.LL..",
        "......BBBB......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_028_cobra", "amber_terminal", [
        "................",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "...BBEBBBBEBB...",
        "...BBBBMMBBBB...",
        "...BBBDBBDBBB...",
        "....BB.BB.BB....",
        ".......BB.......",
        "......BBBB......",
        "....BBBBBBB.....",
        "...BBB..BBBB....",
        "...BB....BBB....",
        "...BBBBABBBB....",
        "....BBBBBBB.....",
        "................",
        "................",
    ]),
    ("mg_seed16_029_ant", "amber_terminal", [
        "................",
        "...N........N...",
        "....N......N....",
        ".....BBBBBB.....",
        ".....BEBBEB.....",
        ".....BBMMBB.....",
        "...LLBBBBBBLL...",
        "..LL..BBBB..LL..",
        ".......BB.......",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BBBABBBB....",
        ".....BBBBBB.....",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_030_fennec", "amber_terminal", [
        "..BB........BB..",
        "..BBB......BBB..",
        "..BBBB....BBBB..",
        "..BBBBBBBBBBBB..",
        "..BBEBBBBBBEBB..",
        "...BBBBMMBBBB...",
        "....BBBABBBB....",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BBB..BBB....",
        "....LLL..LLL....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_031_sandworm", "amber_terminal", [
        "................",
        "....D......D....",
        ".....DBBBBD.....",
        "....BBEBBEBB....",
        "....BMMMMMMB....",
        "....BBBBBBBB....",
        ".....BBABBB.....",
        ".....BBBBBB.....",
        "......BBBB......",
        "......BBBB......",
        ".....BBBBB......",
        "....BBBBB.......",
        "...BBBBB........",
        "....BBBB........",
        "................",
        "................",
    ]),
    ("mg_seed16_032_cat", "amber_terminal", [
        "..B...B.........",
        "..BB.BB.........",
        "..BBBBB.........",
        "..BEEBB.........",
        "..BBBBB.........",
        "..NBMBB.........",
        "...BBBBB........",
        "...BBBBBB.......",
        "...BBABBBB......",
        "...BBBBBBB......",
        "...BBBBBBBB.....",
        "...BBBBBBBB.....",
        "...LL..LL..B....",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_033_ember", "amber_terminal", [
        "................",
        "......F..F......",
        ".....F.FF.F.....",
        "......BBBB......",
        ".....BBBBBB.....",
        ".....BEBBEB.....",
        ".....BBABBB.....",
        "......BMMB......",
        ".......BB.......",
        "......D..D......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_034_obelisk", "amber_terminal", [
        "................",
        "......BBBB......",
        ".....BBBBBB.....",
        ".....BEBBEB.....",
        ".....BBBBBB.....",
        ".....BDBBDB.....",
        ".....BBABBB.....",
        ".....BBBBBB.....",
        ".....BDBBDB.....",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "...BBBBBBBBBB...",
        "................",
        "................",
        "................",
        "................",
    ]),
    # -- crt_blue ---------------------------------------------------------
    ("mg_seed16_035_squid", "crt_blue", [
        "................",
        "......BBBB......",
        ".....BBBBBB.....",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BEBBBBEB....",
        "....BBBABBBB....",
        ".....BMMMMB.....",
        "....L.L..L.L....",
        "....L.L..L.L....",
        "...L..L..L..L...",
        "..L...L..L...L..",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_036_anglerfish", "crt_blue", [
        "....F...........",
        "...NF...........",
        "...N............",
        "..BBBBBBBBB.....",
        ".BEEBBBBBBBBB...",
        ".BMMBBBBABBBBB..",
        ".BBBBBBBBBBBB.L.",
        "..BBBBBBBBBBB.L.",
        "...BBBBBBBB.....",
        "....D..D........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_037_crane", "crt_blue", [
        "................",
        "..BB............",
        "..BEEB..........",
        "..MBB...........",
        "....B...........",
        "....BB..........",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BBBABBBBB...",
        ".....BBBBBBBD...",
        "........J.......",
        "........J.......",
        "........L.......",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_038_nautilus", "crt_blue", [
        "................",
        ".....SSSSSS.....",
        "....SSSSSSSS....",
        "...SSDDDDDDSS...",
        "...SSD....DSS...",
        "...SSD.DD.DSS...",
        "...SSDDDDDDSS...",
        "..BBSSSSSSSS....",
        ".BEEBB..........",
        ".BBBABBB........",
        ".BBBBBBB........",
        ".L.L.L.L........",
        ".L.L.L.L........",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_039_frostbot", "crt_blue", [
        "................",
        ".....D....D.....",
        "....DBBBBBBD....",
        "....BEEBBEEB....",
        "....BBBBBBBB....",
        "..SSBBMMMMBBSS..",
        ".SSBBBBABBBBBSS.",
        ".SS.BBBBBBBB.SS.",
        "....BBBBBBBB....",
        "....BBB..BBB....",
        "....LLL..LLL....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_040_ray", "crt_blue", [
        "................",
        "................",
        "......EBBE......",
        "..BBBBBMMBBBBB..",
        ".BBBBBBBBBBBBBB.",
        "BBBBBBBABBBBBBBB",
        ".BBBBBBBBBBBBBB.",
        "..BBBBBBBBBBBB..",
        "....BBBBBBBB....",
        ".......BB.......",
        ".......BB.......",
        ".......DD.......",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_041_seahorse", "crt_blue", [
        "....DDD.........",
        "....BBBB........",
        "...BEEBB........",
        "..MMBBBB........",
        ".....BBBB.......",
        "......BBBBD.....",
        "......BABB......",
        "......BBBB......",
        ".....BBBB.......",
        ".....BBB........",
        "....BBB.........",
        "....BB..........",
        ".....B..........",
        "....BB..........",
        "................",
        "................",
    ]),
    ("mg_seed16_042_beacon", "crt_blue", [
        "................",
        ".......NN.......",
        "......NBBN......",
        ".....BBBBBB.....",
        "....BEEBBEEB....",
        "SS...BBBBBB...SS",
        ".SSBBBBABBBBSS..",
        "....BBBBBBBB....",
        ".....BBBBBB.....",
        "......BMMB......",
        ".......FF.......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # -- pocket_plum ------------------------------------------------------
    ("mg_seed16_043_bunny", "pocket_plum", [
        "....BB....BB....",
        "....BB....BB....",
        "....BB....BB....",
        "....BBBBBBBB....",
        "...BBEBBBBEBB...",
        "...BBBBMMBBBB...",
        "....BBBBBBBB....",
        ".....BBABBB.....",
        "....BBBBBBBB....",
        "...BBBBBBBBBB...",
        "...BBB....BBB...",
        "...LLL....LLL...",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_044_lunamoth", "pocket_plum", [
        "................",
        "...N........N...",
        "....N......N....",
        "....NEBBBBEN....",
        ".LL..BBMMBB..LL.",
        "LLLLBBBBBBBBLLLL",
        "LLLLBBBABBBBLLLL",
        ".LLLBBBBBBBBLLL.",
        "..LL.BBBBBB.LL..",
        "...LL.BBBB.LL...",
        "...L...BB...L...",
        "...L........L...",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_045_imp", "pocket_plum", [
        "...B........B...",
        "...BB......BB...",
        "....BBBBBBBB....",
        "....BEEBBEEB....",
        ".....BMMMMB.....",
        "..LL.BBBBBB.LL..",
        ".LL.BBBABBBB.LL.",
        "....BBBBBBBB....",
        ".....BBBBBB.....",
        "....BB....BB....",
        "....LL....LL....",
        "......D.........",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_046_fungus", "pocket_plum", [
        "................",
        ".....BBBBBB.....",
        "...BBBBBBBBBB...",
        "..BBDDBBBBDDBB..",
        "..BBBBBBBBBBBB..",
        "......BBBB......",
        ".....BEBBEB.....",
        ".....BBABBB.....",
        ".....BMMMMB.....",
        "......BBBB......",
        ".....F....F.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_047_ghost", "pocket_plum", [
        "................",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BEEBBEEB....",
        "....BBBBBBBB....",
        "....BBMMMMBB....",
        "....BBBABBBB....",
        "....BBBBBBBB....",
        "....BB.BB.BB....",
        ".....B..B..B....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_048_weaver", "pocket_plum", [
        "..D..........D..",
        "...D........D...",
        "....D......D....",
        ".....BBBBBB.....",
        "..LLBEEBBEEBLL..",
        ".LL.BBBBBBBB.LL.",
        ".L..BBBABBBB..L.",
        "....BBBBBBBB....",
        "..LLBBBBBBBBLL..",
        ".LL..BBBBBB..LL.",
        ".....BBBBBB.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_049_koi", "pocket_plum", [
        "................",
        "..BBBBBBBB......",
        ".BEEBBBBBBBB....",
        ".MBBBBBBBBBBBB..",
        ".BBBBBABBBBBBBB.",
        "..BBBBBBBBBB.LL.",
        "...DBBBBBBD..L..",
        "....N....N......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    ("mg_seed16_050_shrine", "pocket_plum", [
        "................",
        "....SSSSSSSS....",
        "...SSSSSSSSSS...",
        ".....BBBBBB.....",
        ".....BEBBEB.....",
        "....BBBBBBBB....",
        "...BBBBABBBBB...",
        "...BBBBBBBBBB...",
        "...BBDBBBBDBB...",
        "...BBBBBBBBBB...",
        "..BBBBBBBBBBBB..",
        ".BBBBBBBBBBBBBB.",
        "................",
        "................",
        "................",
        "................",
    ]),
]


def build_seed_grids() -> list[dict]:
    return [_grid_from_blueprint(*blueprint) for blueprint in BLUEPRINTS]


def build_seed_grids_16() -> list[dict]:
    """The 50-creature 16x16 seed corpus (cycle 09 A2).

    Seeds 001-010 are the ten invariant-scaling pilot exemplars rebuilt
    under corpus identity; 011-050 are authored in BLUEPRINTS_16.
    """
    # Function-level import: invariant_scaling imports corpus_builder at
    # module top, so the reverse import must stay out of module scope.
    from invariant_scaling import PILOT_BLUEPRINTS

    seeds = [
        grid_from_rich_matrix(
            f"mg_seed16_{index:03d}_{grid_id.removeprefix('mg_pilot16_')}",
            rows,
            palette_id,
            size=16,
            source="stage0_hand_authored_blueprint_16x16",
        )
        for index, (grid_id, palette_id, rows) in enumerate(PILOT_BLUEPRINTS, start=1)
    ]
    seeds.extend(
        grid_from_rich_matrix(
            grid_id,
            rows,
            palette_id,
            size=16,
            source="stage0_hand_authored_blueprint_16x16",
        )
        for grid_id, palette_id, rows in BLUEPRINTS_16
    )
    return seeds


def build_invalid_grids_16(seed_grids_16: list[dict]) -> list[dict]:
    """The 16x16 invalid counterexample corpus: the same four structural
    invalidators the 8x8 corpus uses, applied at the ratified scale."""
    return build_invalid_grids(seed_grids_16)


def build_invalid_grids(seed_grids: list[dict]) -> list[dict]:
    invalid: list[dict] = []
    for grid in seed_grids:
        invalid.extend(
            [
                _duplicate_coordinate(grid),
                _out_of_bounds_cell(grid),
                _missing_animation_anchor(grid),
                _missing_organ_cell(grid),
            ]
        )
    return invalid


def write_corpus(seed_dir: Path, invalid_dir: Path) -> None:
    seed_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)

    seeds = build_seed_grids()
    invalid_grids = build_invalid_grids(seeds)
    for grid in seeds:
        _write_json(seed_dir / f"{grid['grid_id']}.json", grid)
    for grid in invalid_grids:
        _write_json(invalid_dir / f"{grid['grid_id']}.json", grid)


def write_corpus_16(seed_dir: Path, invalid_dir: Path) -> None:
    seed_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)

    seeds = build_seed_grids_16()
    invalid_grids = build_invalid_grids_16(seeds)
    for grid in seeds:
        _write_json(seed_dir / f"{grid['grid_id']}.json", grid)
    for grid in invalid_grids:
        _write_json(invalid_dir / f"{grid['grid_id']}.json", grid)


def _grid_from_blueprint(grid_id: str, palette_id: str, rows: list[str]) -> dict:
    if len(rows) != 8 or any(len(row) != 8 for row in rows):
        raise ValueError(f"{grid_id} must be an 8x8 blueprint")

    # strict_tokens: hand-authored blueprints must reject unknown tokens
    # (generator paths in markov_grid/constrained_generator skip them).
    return grid_from_matrix(
        grid_id,
        rows,
        palette_id,
        source="stage0_hand_authored_blueprint",
        strict_tokens=True,
    )


def _duplicate_coordinate(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_duplicate"
    invalid["cells"].append(deepcopy(invalid["cells"][0]))
    return invalid


def _out_of_bounds_cell(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_bounds"
    invalid["cells"][0]["x"] = invalid["grid_size"][0]
    return invalid


def _missing_animation_anchor(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_anchor"
    for cell in invalid["cells"]:
        cell["animation_anchor"] = False
    return invalid


def _missing_organ_cell(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_organ_ref"
    invalid["organs"]["core"]["cells"].append([0, 0])
    return invalid


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dir", type=Path, default=ROOT / "data/seed_grids")
    parser.add_argument("--invalid-dir", type=Path, default=ROOT / "data/invalid_grids")
    parser.add_argument(
        "--seed-dir-16", type=Path, default=ROOT / "data/seed_grids_16x16"
    )
    parser.add_argument(
        "--invalid-dir-16", type=Path, default=ROOT / "data/invalid_grids_16x16"
    )
    args = parser.parse_args()
    write_corpus(args.seed_dir, args.invalid_dir)
    write_corpus_16(args.seed_dir_16, args.invalid_dir_16)


if __name__ == "__main__":
    main()
