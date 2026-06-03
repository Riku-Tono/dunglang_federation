# DungLang Federation 4.0

> **prototype / demo / showcase** — not a complete compiler or formal proof.

DungLang Federation 4.0 is a unified showcase version of the DungLang Federation
prototype line.
It combines the core Federation 1.0 bridge idea with the Civilization v2/v2.1/v3.0
simulation layers: event history, history rewriting, constitution, elections,
civilization metrics, and myth generation.

Older versions are kept in `/versions` as development history.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontends                                              │
│  DungLang 🦍  /  ScatLang 💩  /  SeaIR 🌊  /  YakiimoIR 🍠 │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Odor IR  (shared intermediate representation)          │
│  OdorZeroExpr / OdorSuccExpr / Var / OdorAdd / …        │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  CEK Cave Machine                                       │
│  State(Control, Env, Kont) → OdorSink                   │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Civilization Stack                                     │
│  CivilizationStore → ConstitutionFederation             │
│  ElectionSystem → MythGenerator → CivilizationMetrics   │
└────────────────────────┬────────────────────────────────┘
                         ▼
              outputs/dunglang_federation_4_0_report.json
```

---

## Modules

| Module | From | Description |
|---|---|---|
| Odor IR + CEK Cave Machine | Federation 1.0 | Multiple frontends compile to a shared IR, executed by a CEK-style machine |
| OdorSink / DiplomaticEvent | Federation 1.0 | Odor observation, cross-tribe diplomatic events, banana GC |
| Error Federation | Federation 1.0 | Representative-case check: same IR → same error shape across frontends |
| OdorOptimizer | Civilization v2.0 | Constant-folding pass on odor levels (`zero_elim` / `local_only` / `diplomatic_violation_const`) |
| Ghost Odor / BananaRewrite | Civilization v2.1 | 2PC ghost odor events; temporal history rewriting with banana tokens |
| OdorTypeInference / WitnessCouncil | Civilization v2.2 | Static odor type inference demo; artifact witness council with philosopher-gorilla exclusion |
| Constitution Federation | Civilization v3.0 | Four constitutional articles; violation events emitted on breach |
| Election System | Civilization v3.0 | Council elections with policy factions; verdict for Ghost Odor changes by ruling coalition |
| CivilizationMetrics | Civilization v3.0 | Stability / diplomatic tension / philosophy pollution / myth pressure dashboard |
| MythGenerator | Civilization v3.0 | Erased official history → legend → myth → religion pipeline |

---

## Version History

| Version | Highlight |
|---|---|
| Federation 1.0 | Odor IR bridge · CEK Cave Machine · Error Federation representative cases |
| Civilization v2.0 | OdorOptimizer · Kont Federation · History Federation |
| Civilization v2.1 | Temporal Banana Rewrite · Ghost Odor Archaeology · Causality Leak Detector |
| Civilization v2.2 | OdorTypeInference · TwoPhaseCommit · WitnessCouncil |
| Civilization v3.0 | Constitution Federation · Election System · CivMetrics · MythGenerator |
| **Federation 4.0** | **Unified public showcase of all layers** |

Older versions are preserved in `/versions`.

---

## Running

```bash
python dunglang_federation_4_0.py
```

Output: `outputs/dunglang_federation_4_0_report.json`

The report contains five top-level sections:

```
meta              version info, disclaimer, history
cek_demos         CEK machine runs across all four frontends
odor_optimizer    constant-fold results for representative odor levels
error_federation  paired error-shape checks (trace_equal / error_equal / surface_diff)
civilization      full civilization run: constitution, election, rewrites, metrics, myths, replay
```

---

## Replay Viewer

`dunglang_civilization_replay_viewer.html` is a browser-based dual-pane timeline viewer
for civilization events (built for v2.1, compatible with Federation 4.0 event shapes).

It shows **official history** and **secret log** side by side, with filter buttons per
event kind (`odor 💨`, `diplomatic 🌍`, `ghost 👻`, `rewrite 📜🔥`, `gc 🍌`) and a
configurable replay speed.

Open the file directly in a browser — no server needed.

---

## Scope and Limitations

This project is a **prototype / demo / showcase**.

- The DungLang frontend is a mapping from v0.7 event structures to Odor IR — not a
  full DungLang parser.
- Error Federation checks representative cases only. It is not a full
  formal equivalence proof across distinct syntax parsers.
- BananaGC runs as a post-execution Sink operation in this demo, not as a
  native CEK instruction.
- The philosopher-gorilla exception comparison runs the same IR under two
  frontend names — a minimal surface-diff check, not a cross-parser proof.

---

## Mottos

> Different notation on the surface. Same plumbing underground. — ウホ 🪨
>
> Success is the same. Failure is the same. History disappears. Myth remains. — ウホ 📜🔥
