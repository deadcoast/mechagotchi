# mechas CLI — Design Charter

Date: 2026-07-05. Companion to `mechas-cli.md` (the command reference).
This document is the durable record of the design direction set by the
project owner; every `mechas` command is measured against it. Decision
record 0007 makes it binding.

**Subordination (standing constraint, root `README.md`): this repository
is NOT a CLI application.** `mechas` is a supportive layer for the actual
application — the Mechagotchi Computational Life Engine, the researched
grid-based artificial-life companion engine inspired by *Computational
Life* (arXiv:2406.19108). The CLI serves the engine's workflows; it never
becomes the project, and no CLI ambition may pull development away from
the engine's research-first end goal.

## 1. Mission

The CLI exists to **counteract the frustration and hopelessness a person
feels while troubleshooting a technical problem without development
experience.** Someone opening a terminal mid-problem is already in a
negative, combative mood. Every design choice either de-escalates that
mood or feeds it. `mechas` chooses to de-escalate: it standardizes how
everyone interacts with the application, so there is one well-lit path
instead of improvised mechanics that differ per person and per day.

The founding incident: collecting readability ratings required hand-serving
files over localhost and manually dragging a CSV into the right folder.
Every step of that kind is a place where a user gets stuck, feels stupid,
and gives up. `mechas rate --creatures` replaced all of it with one
command.

## 2. Who it is for

**General users first, developers second.** Developers will use this tool,
but developers do not need to be designed for or standardized for — they
route around friction on their own. General users do need it, and they are
the design target:

- They care more about design, ease of use, and quality of life than
  about speed or developer convention.
- They care most that **an advanced tool feels advanced to use without
  making them feel stupid** — the tool should make them feel smart.
- They do not want to open a CLI and see a cookie-cutter template built
  for developers.

Equally binding in the other direction: the CLI must **not** be childish
or over-simplified. It stays technical, yet catered — targeted to the use
case, developed with quality of life, so the user has to learn a little
but never gets lost in frivolous development standards. Users should feel
smart, not like babies.

## 3. The explicit trade

**This CLI does not optimize for maximum speed or minimal keystrokes.**
It deliberately sacrifices small speed margins for maximum developed
quality of life and UI design. Standardized use that minimizes user error
is worth more than milliseconds. When a shortcut and a clearer experience
conflict, the clearer experience wins — that is the point of the tool, not
a compromise.

This is also why **Typer + Rich were specified over plain argparse**: the
plain Python CLI stack is faster and templated for developer
understanding and standardization — and that is exactly the audience this
tool is *not* built for. Typer gives a discoverable, self-documenting
command tree; Rich gives typographic hierarchy, color with meaning, and
layout — the raw material of a catered experience.

## 4. The three pillars

Every command is reviewed against all three before it ships:

- **1-A · UI design** — The terminal output is designed, not emitted. One
  theme (the LCD-handheld look, drawn from the project's own creature
  palettes) shared by every command via `theme.py`: a consistent banner,
  key-value status tables, next-step panels, semantic color (green = good,
  amber = waiting on you, red = problem). Output must survive hostile
  terminals: a legacy Windows console gets degraded glyphs, never a crash.
- **2-A · Quality-of-life development** — Commands complete whole tasks,
  not fragments. The rating session serves, opens, receives, saves,
  backs up what it would overwrite, and runs the gate — the user never
  moves a file. Destructive-adjacent actions self-protect
  (backup-before-overwrite). Wherever the tool knows the next step, it
  says so explicitly rather than leaving the user to guess.
- **3-A · CLI ease of use** — The command grammar is one shape everywhere:
  `mechas` (main command) → `rate` (function/tool) → `--creatures`
  (flag/option). Names come from how the application actually operates,
  in user language — it is `--creatures`, not `--readability-calibration-
  samples`, because the user is rating creatures. Running a command with
  no flags is never an error: it explains its targets and shows copyable
  examples. Errors say what went wrong and what to do, never a stack
  trace.

## 5. Naming

The main command is **`mechas`**: directly on theme for Mechagotchi, not
an industry-standard word (so it collides with nothing and carries no
imported expectations), and general enough that it will not constrict any
future additions to the tool. Subcommands are verbs for tasks (`rate`),
flags are the user-language nouns and switches of that task
(`--creatures`, `--autoexport`).

## 6. Modularity

One workflow, one module (`workflows/rate.py`); one theme module every
command must use; the server and workspace-resolution pieces stay
stdlib-only and independently testable. New capability = new workflow
module + a registration line — the foundation is designed robust and
comprehensive precisely because the tool is small today: it is the
beginning of the CLI that supports the whole application, and it should
grow by addition, not rework.

## 7. What this is not

- Not the application: the repository is not a CLI application; `mechas`
  is its supportive layer. The engine is the project.
- Not a research lab: no `_stage0.json` evidence obligations for UI code
  (the tools it *invokes* keep theirs).
- Not an optimizer: no flag exists to shave a step at the cost of
  clarity.
- Not a substitute for humans: the CLI moves and validates evidence but
  never fabricates it — rating rows come only from people, and the gates
  stay the judges.

## Sources

- `docs/cli/mechas-cli.md`
- `research/decision_records/0007-mechas-companion-cli.md`
- `tools/mechas_cli/src/mechas_cli/theme.py`
- `tools/mechas_cli/src/mechas_cli/workflows/rate.py`
- `research/experiment_reports/2026-07-05-slip-readability-rating-tool.md`
