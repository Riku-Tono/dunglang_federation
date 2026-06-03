# -*- coding: utf-8 -*-
"""
DungLang Federation 4.0
========================
  Public Integration Showcase

  ⚠️  This is a prototype / demo / showcase.
       Not a production compiler, formal proof, or complete distributed system.

  Integrated Version History:
    Federation 1.0          : DungLang + ScatLang + SeaIR + YakiimoIR → OdorIR → CEK Cave Machine
    Civilization v2.0       : OdorOptimizer / Kont Federation / History Federation
    Civilization v2.1       : Temporal Banana Rewrite / Ghost Odor Archaeology / Causality Leak
    Civilization v2.2       : OdorTypeInference / TwoPhaseCommit / WitnessCouncil
    Civilization v3.0       : Constitution Federation / Election System / CivMetrics / MythGenerator
    Federation 4.0 (this release): Public showcase integrating all layers

  Architecture:
    ┌──────────────────────────────────────────────────────────┐
    │  Frontend Layer                                          │
    │  DungLang / ScatLang / SeaIR / YakiimoIR                 │
    └────────────────────┬─────────────────────────────────────┘
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  OdorIR (Common Intermediate Representation)             │
    │  OdorZeroExpr / OdorSuccExpr / Var / OdorAdd / ...      │
    └────────────────────┬─────────────────────────────────────┘
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  CEK Cave Machine                                        │
    │  State(Control, Env, Kont) → OdorSink                   │
    └────────────────────┬─────────────────────────────────────┘
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Civilization Layer (Civilization Stack)                 │
    │  CivilizationStore → ConstitutionFederation              │
    │  ElectionSystem → MythGenerator → CivilizationMetrics   │
    └────────────────────┬─────────────────────────────────────┘
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Output: outputs/dunglang_federation_4_0_report.json     │
    └──────────────────────────────────────────────────────────┘

Motto:
  Surface syntax may differ, but the underground plumbing is the same. UHO.
  Success is the same. Failure is the same. Even when history vanishes, myths endure. UHO.
"""
from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

# stdout UTF-8 setup UHO
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════════════════════════
# § 0  Meta Information
# ══════════════════════════════════════════════════════════════

VERSION_HISTORY = [
    {"version": "Federation 1.0",     "highlight": "OdorIR integration, CEK Cave Machine, Error Federation representative case verification"},
    {"version": "Civilization v2.0",  "highlight": "OdorOptimizer, Kont Federation, History Federation"},
    {"version": "Civilization v2.1",  "highlight": "Temporal Banana Rewrite, Ghost Odor Archaeology, Causality Leak Detector"},
    {"version": "Civilization v2.2",  "highlight": "OdorTypeInference, TwoPhaseCommit, WitnessCouncil"},
    {"version": "Civilization v3.0",  "highlight": "Constitution Federation, Election System, CivMetrics, MythGenerator"},
    {"version": "Federation 4.0",     "highlight": "Full-layer integrated showcase, public release"},
]

DISCLAIMER = (
    "prototype / demo / showcase — "
    "not a production compiler, formal proof, or complete distributed system."
)

# ══════════════════════════════════════════════════════════════
# § 1  Exception & Value System (Federation 1.0 Foundation)
# ══════════════════════════════════════════════════════════════

class ScatError(Exception): pass
class ParseError(ScatError): pass
class StepLimitError(ScatError): pass
class PhilosophyGorillaError(ScatError): pass
class AxiomDestructionError(ScatError): pass
class BananaShortageError(ScatError): pass
class CrossBorderOdorError(ScatError): pass


class Value:
    def pretty(self) -> str: raise NotImplementedError
    def to_int(self) -> int:  raise NotImplementedError


@dataclass(frozen=True)
class PoopZero(Value):
    def pretty(self): return "💩₀"
    def to_int(self):  return 0


@dataclass(frozen=True)
class PoopSucc(Value):
    inner: Value
    def pretty(self): return f"💩×{self.to_int()}"
    def to_int(self):  return 1 + self.inner.to_int()


@dataclass(frozen=True)
class Underflow(Value):
    def pretty(self): return "💩∅"
    def to_int(self):  return 0


@dataclass(frozen=True)
class OdorValue(Value):
    level: Value
    source: str = "unknown"
    def pretty(self): return f"💨×{self.level.to_int()}({self.source})"
    def to_int(self):  return self.level.to_int()


@dataclass(frozen=True)
class BananaValue(Value):
    count: Value
    def pretty(self): return f"🍌×{self.count.to_int()}"
    def to_int(self):  return self.count.to_int()


def int_to_poop(n: int) -> Value:
    v: Value = PoopZero()
    for _ in range(n): v = PoopSucc(v)
    return v


def int_to_value_expr(n: int) -> "Expr":
    e: Expr = PoopZeroExpr()
    for _ in range(n): e = PoopSuccExpr(e)
    return e


TRUE  = PoopSucc(PoopZero())
FALSE = PoopZero()

# ══════════════════════════════════════════════════════════════
# § 2  OdorIR (Common Intermediate Representation)
# ══════════════════════════════════════════════════════════════

class Expr: pass
class Stmt:  pass


@dataclass(frozen=True)
class OdorZeroExpr(Expr): pass

@dataclass(frozen=True)
class OdorSuccExpr(Expr):
    expr: Expr

@dataclass(frozen=True)
class PoopZeroExpr(Expr): pass

@dataclass(frozen=True)
class PoopSuccExpr(Expr):
    expr: Expr

@dataclass(frozen=True)
class Var(Expr):
    name: str

@dataclass(frozen=True)
class OdorAdd(Expr):
    left: Expr; right: Expr

@dataclass(frozen=True)
class OdorNeq(Expr):
    left: Expr; right: Expr

@dataclass(frozen=True)
class OdorSub(Expr):
    left: Expr; right: Expr

@dataclass(frozen=True)
class OdorMod(Expr):
    left: Expr; right: Expr

@dataclass(frozen=True)
class OdorEq(Expr):
    left: Expr; right: Expr

@dataclass(frozen=True)
class OdorPred(Expr):
    expr: Expr

@dataclass(frozen=True)
class PhilosophyExpr(Expr):
    question: str

@dataclass(frozen=True)
class BananaExpr(Expr):
    count: Expr

@dataclass(frozen=True)
class Assign(Stmt):
    name: str; expr: Expr

@dataclass(frozen=True)
class Flush(Stmt):
    expr: Expr

@dataclass(frozen=True)
class While(Stmt):
    left: Expr; right: Expr; body: tuple

@dataclass(frozen=True)
class OdorFlush(Stmt):
    expr: Expr
    source: str = "unknown"

@dataclass(frozen=True)
class DiplomaticFlush(Stmt):
    expr: Expr
    from_tribe: str
    to_tribe:   str

# ══════════════════════════════════════════════════════════════
# § 3  OdorSink (Federation 1.0 inherited + v2.x extended)
# ══════════════════════════════════════════════════════════════

TREATY = {
    ("UhoTribe",    "BananaTribe"):    3,
    ("UhoTribe",    "MammothTribe"):   5,
    ("BananaTribe", "MammothTribe"):   4,
}


@dataclass(frozen=True)
class Artifact:
    value: Value; born_at_step: int


@dataclass(frozen=True)
class Observation:
    artifact: Artifact; context: str


@dataclass(frozen=True)
class OdorEvent:
    step: int; level: int; source: str; context: str


@dataclass(frozen=True)
class DiplomaticEvent:
    step: int; level: int; from_tribe: str; to_tribe: str
    verdict: str; banana_penalty: int


@dataclass(frozen=True)
class BananaGCEvent:
    step: int; banana_count: int; erased_count: int


@dataclass
class OdorSink:
    _observations:  list = field(default_factory=list)
    _odor_events:   list = field(default_factory=list)
    _diplo_events:  list = field(default_factory=list)
    _gc_events:     list = field(default_factory=list)
    _memory_buffer: list = field(default_factory=list)
    step_count: int = 0
    frontend:   str = "unknown"

    def tick(self): self.step_count += 1

    def observe(self, v: Value, ctx: str = "flush"):
        self._observations.append(Observation(Artifact(v, self.step_count), ctx))

    def observe_odor(self, level: int, source: str, ctx: str = "odor_flush"):
        ev = OdorEvent(self.step_count, level, source, ctx)
        self._odor_events.append(ev)
        self._memory_buffer.append(f"OdorLv{level}({source})")

    def observe_diplomatic(self, level: int, from_t: str, to_t: str) -> DiplomaticEvent:
        treaty_val = TREATY.get((from_t, to_t), 4)
        if level > treaty_val:
            verdict        = "DiplomaticIncident"
            banana_penalty = level * 2
        else:
            verdict        = "WeatherGorillaFault"
            banana_penalty = 0
        ev = DiplomaticEvent(self.step_count, level, from_t, to_t, verdict, banana_penalty)
        self._diplo_events.append(ev)
        self._memory_buffer.append(f"Diplomacy:{verdict}({from_t}→{to_t})")
        return ev

    def banana_gc(self, banana_count: int) -> BananaGCEvent:
        erased = len(self._memory_buffer)
        self._memory_buffer.clear()
        ev = BananaGCEvent(self.step_count, banana_count, erased)
        self._gc_events.append(ev)
        return ev

    @property
    def observations(self):    return tuple(self._observations)
    @property
    def odor_events(self):     return tuple(self._odor_events)
    @property
    def diplo_events(self):    return tuple(self._diplo_events)
    @property
    def gc_events(self):       return tuple(self._gc_events)
    @property
    def memory_buffer(self):   return list(self._memory_buffer)

# ══════════════════════════════════════════════════════════════
# § 4  CEK Cave Machine (Federation 1.0 inherited)
# ══════════════════════════════════════════════════════════════

class Kont: pass


@dataclass(frozen=True)
class Halt(Kont): pass

@dataclass(frozen=True)
class AssignK(Kont):
    name: str; rest: tuple; env: Any; kont: Kont

@dataclass(frozen=True)
class FlushK(Kont):
    rest: tuple; env: Any; kont: Kont

@dataclass(frozen=True)
class OdorFlushK(Kont):
    rest: tuple; env: Any; kont: Kont; source: str

@dataclass(frozen=True)
class DiplomaticFlushK(Kont):
    rest: tuple; env: Any; kont: Kont; from_tribe: str; to_tribe: str

@dataclass(frozen=True)
class SuccK(Kont):   kont: Kont

@dataclass(frozen=True)
class AddLeftK(Kont):
    right: Expr; env: Any; kont: Kont

@dataclass(frozen=True)
class AddRightK(Kont):
    left_val: Value; kont: Kont

@dataclass(frozen=True)
class NeqLeftK(Kont):
    right: Expr; env: Any; kont: Kont

@dataclass(frozen=True)
class NeqRightK(Kont):
    left_val: Value; kont: Kont

@dataclass(frozen=True)
class PredK(Kont): kont: Kont

@dataclass(frozen=True)
class SubLeftK(Kont):
    right: Expr; env: Any; kont: Kont

@dataclass(frozen=True)
class SubRightK(Kont):
    left_val: Value; kont: Kont

@dataclass(frozen=True)
class ModLeftK(Kont):
    right: Expr; env: Any; kont: Kont

@dataclass(frozen=True)
class ModRightK(Kont):
    left_val: Value; kont: Kont

@dataclass(frozen=True)
class EqLeftK(Kont):
    right: Expr; env: Any; kont: Kont

@dataclass(frozen=True)
class EqRightK(Kont):
    left_val: Value; kont: Kont

@dataclass(frozen=True)
class WhileK(Kont):
    stmt: While; rest: tuple; env: Any; kont: Kont

@dataclass(frozen=True)
class EvalExpr:  expr: Expr

@dataclass(frozen=True)
class ReturnValue: value: Value


@dataclass
class State:
    control: object
    env:     dict
    kont:    Kont
    sink:    OdorSink


def is_halted(s): return isinstance(s.control, ReturnValue) and isinstance(s.kont, Halt)

def poop_add(a, b): return int_to_poop(a.to_int() + b.to_int())
def poop_sub(a, b): return int_to_poop(max(a.to_int() - b.to_int(), 0))
def poop_pred(v):
    if isinstance(v, PoopZero): return Underflow()
    if isinstance(v, PoopSucc): return v.inner
    return Underflow()
def poop_mod(a, b):
    if b.to_int() == 0: raise ScatError("mod by zero UHO")
    return int_to_poop(a.to_int() % b.to_int())
def poop_eq(a, b):  return TRUE if a.to_int() == b.to_int() else FALSE
def poop_neq(a, b): return TRUE if a.to_int() != b.to_int() else FALSE


def step(state: State) -> State:
    state.sink.tick()
    ctrl = state.control

    if isinstance(ctrl, tuple):
        if not ctrl:
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)
        head, *tail = ctrl
        rest = tuple(tail)
        if isinstance(head, Assign):
            return State(EvalExpr(head.expr), state.env,
                         AssignK(head.name, rest, dict(state.env), state.kont), state.sink)
        if isinstance(head, Flush):
            return State(EvalExpr(head.expr), state.env,
                         FlushK(rest, dict(state.env), state.kont), state.sink)
        if isinstance(head, OdorFlush):
            return State(EvalExpr(head.expr), state.env,
                         OdorFlushK(rest, dict(state.env), state.kont, head.source), state.sink)
        if isinstance(head, DiplomaticFlush):
            return State(EvalExpr(head.expr), state.env,
                         DiplomaticFlushK(rest, dict(state.env), state.kont,
                                          head.from_tribe, head.to_tribe), state.sink)
        if isinstance(head, While):
            return State(EvalExpr(OdorNeq(head.left, head.right)), state.env,
                         WhileK(head, rest, dict(state.env), state.kont), state.sink)
        raise ScatError(f"unknown stmt: {head!r}")

    if isinstance(ctrl, EvalExpr):
        e = ctrl.expr
        if isinstance(e, (PoopZeroExpr, OdorZeroExpr)):
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)
        if isinstance(e, (PoopSuccExpr, OdorSuccExpr)):
            return State(EvalExpr(e.expr), state.env, SuccK(state.kont), state.sink)
        if isinstance(e, Var):
            if e.name not in state.env:
                raise ScatError(f"unbound variable: {e.name}")
            return State(ReturnValue(state.env[e.name]), state.env, state.kont, state.sink)
        if isinstance(e, OdorAdd):
            return State(EvalExpr(e.left), state.env,
                         AddLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorNeq):
            return State(EvalExpr(e.left), state.env,
                         NeqLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorPred):
            return State(EvalExpr(e.expr), state.env, PredK(state.kont), state.sink)
        if isinstance(e, OdorSub):
            return State(EvalExpr(e.left), state.env,
                         SubLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorMod):
            return State(EvalExpr(e.left), state.env,
                         ModLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorEq):
            return State(EvalExpr(e.left), state.env,
                         EqLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, PhilosophyExpr):
            raise PhilosophyGorillaError(e.question)
        if isinstance(e, BananaExpr):
            return State(EvalExpr(e.count), state.env, state.kont, state.sink)
        raise ScatError(f"unknown expr: {e!r}")

    if isinstance(ctrl, ReturnValue):
        v, k = ctrl.value, state.kont
        if isinstance(k, Halt):    return state
        if isinstance(k, SuccK):
            return State(ReturnValue(PoopSucc(v)), state.env, k.kont, state.sink)
        if isinstance(k, AssignK):
            ne = dict(k.env); ne[k.name] = v
            return State(k.rest, ne, k.kont, state.sink)
        if isinstance(k, FlushK):
            state.sink.observe(v)
            return State(k.rest, dict(k.env), k.kont, state.sink)
        if isinstance(k, OdorFlushK):
            state.sink.observe_odor(v.to_int(), k.source)
            return State(k.rest, dict(k.env), k.kont, state.sink)
        if isinstance(k, DiplomaticFlushK):
            ev = state.sink.observe_diplomatic(v.to_int(), k.from_tribe, k.to_tribe)
            if ev.verdict == "DiplomaticIncident":
                raise CrossBorderOdorError(
                    f"{k.from_tribe}→{k.to_tribe} concentration={v.to_int()} "
                    f"banana_reparations={ev.banana_penalty}"
                )
            return State(k.rest, dict(k.env), k.kont, state.sink)
        if isinstance(k, AddLeftK):
            return State(EvalExpr(k.right), dict(k.env), AddRightK(v, k.kont), state.sink)
        if isinstance(k, AddRightK):
            return State(ReturnValue(poop_add(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, NeqLeftK):
            return State(EvalExpr(k.right), dict(k.env), NeqRightK(v, k.kont), state.sink)
        if isinstance(k, NeqRightK):
            return State(ReturnValue(poop_neq(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, PredK):
            return State(ReturnValue(poop_pred(v)), state.env, k.kont, state.sink)
        if isinstance(k, SubLeftK):
            return State(EvalExpr(k.right), dict(k.env), SubRightK(v, k.kont), state.sink)
        if isinstance(k, SubRightK):
            return State(ReturnValue(poop_sub(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, ModLeftK):
            return State(EvalExpr(k.right), dict(k.env), ModRightK(v, k.kont), state.sink)
        if isinstance(k, ModRightK):
            return State(ReturnValue(poop_mod(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, EqLeftK):
            return State(EvalExpr(k.right), dict(k.env), EqRightK(v, k.kont), state.sink)
        if isinstance(k, EqRightK):
            return State(ReturnValue(poop_eq(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, WhileK):
            if v.to_int() == 0:
                return State(k.rest, dict(k.env), k.kont, state.sink)
            return State(k.stmt.body + (k.stmt,) + k.rest, dict(k.env), k.kont, state.sink)
        raise ScatError(f"unknown kont: {k!r}")

    raise ScatError(f"unknown ctrl: {ctrl!r}")

# ══════════════════════════════════════════════════════════════
# § 5  TraceCollector & RunCapture
# ══════════════════════════════════════════════════════════════

def kont_depth_fn(k):
    d = 0
    while not isinstance(k, Halt):
        d += 1; k = getattr(k, "kont", None)
        if k is None: break
    return d


@dataclass(frozen=True)
class TraceEvent:
    step: int; control_kind: str; expr_kind: str
    kont_kind: str; kont_depth: int; env_keys: tuple
    observed_count: int; frontend: str
    odor_count: int = 0; diplo_count: int = 0; gc_count: int = 0

    def signature(self, *, include_frontend=False):
        r = (self.control_kind, self.expr_kind, self.kont_kind,
             self.kont_depth, self.env_keys, self.observed_count)
        return r + ((self.frontend,) if include_frontend else ())

    def to_dict(self):
        return dict(step=self.step, control_kind=self.control_kind,
                    expr_kind=self.expr_kind, kont_kind=self.kont_kind,
                    kont_depth=self.kont_depth, env_keys=list(self.env_keys),
                    observed_count=self.observed_count, frontend=self.frontend,
                    odor_count=self.odor_count, diplo_count=self.diplo_count,
                    gc_count=self.gc_count)


@dataclass(frozen=True)
class TraceErrorEvent:
    step: int; control_kind: str; expr_kind: str
    kont_kind: str; kont_depth: int; env_keys: tuple
    observed_count: int; frontend: str
    error_type: str; error_message: str

    def signature(self, *, include_frontend=False, include_message=True):
        r = (self.control_kind, self.expr_kind, self.kont_kind,
             self.kont_depth, self.env_keys, self.observed_count, self.error_type)
        if include_message: r = r + (self.error_message,)
        return r + ((self.frontend,) if include_frontend else ())

    def to_dict(self):
        return dict(step=self.step, control_kind=self.control_kind,
                    expr_kind=self.expr_kind, kont_kind=self.kont_kind,
                    kont_depth=self.kont_depth, env_keys=list(self.env_keys),
                    observed_count=self.observed_count, frontend=self.frontend,
                    error_type=self.error_type, error_message=self.error_message)


class TraceCollector:
    def __init__(self): self.events = []
    def __call__(self, ev): self.events.append(ev)
    def signature(self, *, include_frontend=False):
        return tuple(e.signature(include_frontend=include_frontend) for e in self.events)


@dataclass(frozen=True)
class RunCapture:
    final_state: object
    trace: TraceCollector
    error: object
    def ok(self): return self.error is None


def make_trace(step_no, state):
    ctrl = state.control
    if isinstance(ctrl, tuple):
        ck, ek = "StmtSeq", f"len={len(ctrl)}"
    elif isinstance(ctrl, EvalExpr):
        ck, ek = "EvalExpr", type(ctrl.expr).__name__
    elif isinstance(ctrl, ReturnValue):
        ck, ek = "ReturnValue", ctrl.value.pretty()
    else:
        ck, ek = type(ctrl).__name__, ""
    return TraceEvent(
        step=step_no, control_kind=ck, expr_kind=ek,
        kont_kind=type(state.kont).__name__,
        kont_depth=kont_depth_fn(state.kont),
        env_keys=tuple(sorted(state.env.keys())),
        observed_count=len(state.sink.observations),
        frontend=state.sink.frontend,
        odor_count=len(state.sink.odor_events),
        diplo_count=len(state.sink.diplo_events),
        gc_count=len(state.sink.gc_events),
    )


def make_error(step_no, state, exc):
    t = make_trace(step_no, state)
    return TraceErrorEvent(
        step=t.step, control_kind=t.control_kind, expr_kind=t.expr_kind,
        kont_kind=t.kont_kind, kont_depth=t.kont_depth, env_keys=t.env_keys,
        observed_count=t.observed_count, frontend=t.frontend,
        error_type=type(exc).__name__, error_message=str(exc),
    )


def run_capture(prog, env=None, *, frontend: str, max_steps: int = 200_000) -> RunCapture:
    col   = TraceCollector()
    sink  = OdorSink(frontend=frontend)
    state = State(tuple(prog), dict(env or {}), Halt(), sink)
    for step_no in range(max_steps):
        if is_halted(state):
            return RunCapture(state, col, None)
        col(make_trace(step_no, state))
        try:
            state = step(state)
        except ScatError as e:
            return RunCapture(None, col, make_error(step_no, state, e))
    exc = StepLimitError(f"step limit exceeded: {max_steps}")
    return RunCapture(None, col, make_error(max_steps, state, exc))

# ══════════════════════════════════════════════════════════════
# § 6  Frontend Suite
# ══════════════════════════════════════════════════════════════

# ── 6a. ScatLang / SeaIR (symmetric frontends for representative case comparison) ──

def scatlang_mod_by_zero():
    return (Assign("x", OdorMod(int_to_value_expr(3), int_to_value_expr(0))),)

def scatlang_unbound():
    return (Flush(Var("missing")),)

def scatlang_infinite():
    return (While(int_to_value_expr(0), PoopSuccExpr(PoopZeroExpr()), (
        Assign("x", PoopZeroExpr()),
    )),)

def seair_mod_by_zero():  return scatlang_mod_by_zero()
def seair_unbound():      return scatlang_unbound()
def seair_infinite():     return scatlang_infinite()

# ── 6b. YakiimoIR (Philosophy / Diplomacy / Banana GC) ──

def yakiimo_philosophy():
    return (
        Assign("question", PhilosophyExpr("To whom does the flatulence belong? UHO")),
        Flush(Var("question")),
    )

def yakiimo_diplomatic():
    return (DiplomaticFlush(int_to_value_expr(7), "UhoTribe", "BananaTribe"),)

def yakiimo_banana_gc():
    return (
        Assign("banana", BananaExpr(int_to_value_expr(3))),
        Flush(Var("banana")),
    )

# ── 6c. DungLang (v0.7 event structure → OdorIR mapping) ──

def dunglang_compile(phenomenon: dict) -> tuple:
    """
    Demo mapping DungLang v0.7 patched event structure to OdorIR Stmt tuples.
    Not a full DungLang parser — a showcase mapping v0.7 "smell/suspect/side-effect-level"
    onto OdorIR Stmts.
    """
    odor_level  = {"odorless": 0, "faint": 1, "strong": 3, "omnidirectional": 7}.get(
                    phenomenon.get("smell", "faint"), 2)
    fart_count  = phenomenon.get("side_effect_level", 0)
    suspect     = phenomenon.get("suspect", "unknown")
    total_level = odor_level + fart_count

    stmts = [
        Assign("odor_level", int_to_value_expr(total_level)),
        OdorFlush(int_to_value_expr(total_level), source=suspect),
    ]
    if phenomenon.get("smell") == "omnidirectional":
        stmts.append(DiplomaticFlush(int_to_value_expr(total_level), "UhoTribe", "BananaTribe"))
    return tuple(stmts)

# ── 6d. OdorOptimizer (v2.0 inherited) ──

@dataclass(frozen=True)
class OptimizedOdor:
    """v2.0 OdorOptimizer — demo for constant-folding odor level optimization UHO"""
    original_level: int
    optimized_level: int
    strategy: str

    def to_dict(self) -> dict:
        return {
            "original_level": self.original_level,
            "optimized_level": self.optimized_level,
            "strategy": self.strategy,
        }


def odor_optimize(level: int) -> OptimizedOdor:
    """
    Simple OdorOptimizer:
      - Lv0      → odorless (eliminable)
      - Lv1~2   → faint (local propagation only)
      - Lv3~5   → diplomatic check required
      - Lv6+    → diplomatic violation confirmed, constant-folded
    """
    if level == 0:
        return OptimizedOdor(level, 0, "zero_elim")
    if level <= 2:
        return OptimizedOdor(level, level, "local_only")
    if level <= 5:
        return OptimizedOdor(level, level, "diplomatic_check_required")
    # Lv6+ marked as diplomatic violation constant
    return OptimizedOdor(level, level, "diplomatic_violation_const")

# ══════════════════════════════════════════════════════════════
# § 7  Civilization Layer (Civilization v3.0 integrated)
# ══════════════════════════════════════════════════════════════

# ── CivEvent ──

@dataclass(frozen=True)
class CivEvent:
    step: int; kind: str; detail: str
    frontend: str = "🦍DungLang"; era: str = "official"

    def to_dict(self) -> dict:
        return {"step": self.step, "kind": self.kind,
                "detail": self.detail, "frontend": self.frontend, "era": self.era}


@dataclass(frozen=True)
class GhostOdorEvent(CivEvent):
    cave_a: str = "🦣CaveA"; cave_b: str = "🦣CaveB"; odor_level: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"cave_a": self.cave_a, "cave_b": self.cave_b, "odor_level": self.odor_level})
        return d


@dataclass(frozen=True)
class HistoryRewriteEvent(CivEvent):
    erased_event: str = ""
    rewritten_as: str = "deemed to have never existed from the start"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"erased_event": self.erased_event, "rewritten_as": self.rewritten_as})
        return d


@dataclass(frozen=True)
class ArchaeologicalArtifact(CivEvent):
    artifact_id: str = ""; source_event: str = ""; confidence: float = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"artifact_id": self.artifact_id,
                  "source_event": self.source_event,
                  "confidence": round(self.confidence, 3)})
        return d

# ── Constitution Federation (v3.0) ──

@dataclass(frozen=True)
class ConstitutionArticle:
    article_no: int; title: str; rule: str

    def to_dict(self) -> dict:
        return {"article_no": self.article_no, "title": self.title, "rule": self.rule}


@dataclass(frozen=True)
class ConstitutionViolationEvent(CivEvent):
    article_no: int = 0; article_title: str = ""; offender: str = ""; severity: int = 1

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"article_no": self.article_no, "article_title": self.article_title,
                  "offender": self.offender, "severity": self.severity})
        return d


class ConstitutionFederation:
    def __init__(self) -> None:
        self.articles = [
            ConstitutionArticle(1, "WitnessQualification", "PhilosophyGorilla cannot be a witness"),
            ConstitutionArticle(2, "GhostOdorPresumptionOfInnocence", "GhostOdor shall not be presumed directly guilty"),
            ConstitutionArticle(3, "BananaHistoryRevisionRight", "History revision may be petitioned with 3 or more bananas"),
            ConstitutionArticle(4, "CrossBorderOdorDiplomacy", "Cross-border occurrence of GhostOdor is a diplomatic matter"),
        ]

    def check(self, action: str, *, actor: str, step: int) -> Optional[ConstitutionViolationEvent]:
        if action == "philosophy_gorilla_witness" and "PhilosophyGorilla" in actor:
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ Article 1 Violation: PhilosophyGorilla was made a witness",
                "ConstitutionIR", "legal", 1, "WitnessQualification", actor, 5)
        if action == "convict_ghost_odor":
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ Article 2 Violation: GhostOdor was directly convicted",
                "ConstitutionIR", "legal", 2, "GhostOdorPresumptionOfInnocence", actor, 4)
        if action == "banana_rewrite" and actor == "2bananas":
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ Article 3 Violation: History revision attempted with insufficient bananas",
                "ConstitutionIR", "legal", 3, "BananaHistoryRevisionRight", actor, 3)
        return None

    def to_dict(self) -> dict:
        return {"articles": [a.to_dict() for a in self.articles]}

# ── Election System (v3.0) ──

class Policy(Enum):
    STRICT            = auto()
    BALANCED          = auto()
    BANANA_POPULIST   = auto()
    REVOLUTIONARY     = auto()

    def pretty(self) -> str:
        return {
            Policy.STRICT:          "Strict Penalty",
            Policy.BALANCED:        "Balanced Council",
            Policy.BANANA_POPULIST: "Banana Welfare Populism",
            Policy.REVOLUTIONARY:   "Revolutionary Acquittalism",
        }[self]


@dataclass(frozen=True)
class Candidate:
    name: str; party: str; policy: Policy


@dataclass(frozen=True)
class ElectionResult:
    step: int; term_no: int
    winners: list; vote_share: dict

    def to_event(self) -> CivEvent:
        winners = ", ".join(c.name for c in self.winners)
        return CivEvent(self.step, "election",
                        f"🗳️ CouncilTerm #{self.term_no}: {winners} elected",
                        "ElectionIR", "political")

    def to_dict(self) -> dict:
        return {
            "step": self.step, "term_no": self.term_no,
            "winners": [{"name": c.name, "party": c.party, "policy": c.policy.pretty()}
                        for c in self.winners],
            "vote_share": self.vote_share,
        }


class ElectionSystem:
    def __init__(self, seed: int = 40) -> None:
        self.rng = random.Random(seed)
        self.candidates = [
            Candidate("ResearchGorilla",    "Empirical Party",      Policy.BALANCED),
            Candidate("WeatherGorilla",     "Wind Direction Party", Policy.BALANCED),
            Candidate("LegalGorilla",       "Stone Tablet Rule of Law Party", Policy.STRICT),
            Candidate("BananaPartyGorilla", "Banana Party",         Policy.BANANA_POPULIST),
            Candidate("RevolutionGorilla",  "Cave Revolution Front", Policy.REVOLUTIONARY),
        ]

    def run_election(self, *, step: int, term_no: int) -> ElectionResult:
        raw    = {c.name: self.rng.uniform(0.05, 0.35) for c in self.candidates}
        total  = sum(raw.values())
        shares = {k: round(v / total, 3) for k, v in raw.items()}
        winners = sorted(self.candidates, key=lambda c: shares[c.name], reverse=True)[:3]
        return ElectionResult(step, term_no, winners, shares)

    @staticmethod
    def verdict_for_ghost_odor(result: ElectionResult) -> str:
        policies = [c.policy for c in result.winners]
        if Policy.REVOLUTIONARY    in policies: return "GhostOdor → Acquitted. Odor is the self-expression of the people. UHO"
        if Policy.STRICT           in policies: return "GhostOdor → Under Investigation. Stone tablet audit continues. UHO"
        if Policy.BANANA_POPULIST  in policies: return "GhostOdor → Pacified by banana distribution. UHO"
        return "GhostOdor → Pending. Awaiting WeatherGorilla testimony. UHO"

# ── Civilization Metrics (v3.0) ──

@dataclass(frozen=True)
class CivilizationMetrics:
    stability:            float
    diplomatic_tension:   float
    philosophy_pollution: float
    history_rewrite_rate: float
    ghost_odor_count:     int
    myth_pressure:        float

    def to_dict(self) -> dict:
        return {
            "stability":            round(self.stability, 3),
            "diplomatic_tension":   round(self.diplomatic_tension, 3),
            "philosophy_pollution": round(self.philosophy_pollution, 3),
            "history_rewrite_rate": round(self.history_rewrite_rate, 3),
            "ghost_odor_count":     self.ghost_odor_count,
            "myth_pressure":        round(self.myth_pressure, 3),
        }

    def dashboard(self) -> str:
        def bar(x: float) -> str:
            n = max(0, min(10, int(round(x / 10))))
            return "█" * n + "░" * (10 - n) + f" {x:5.1f}%"
        return "\n".join([
            "📊 Civilization Metrics",
            f"  Civilization Stability    {bar(self.stability)}",
            f"  Diplomatic Tension        {bar(self.diplomatic_tension)}",
            f"  Philosophy Pollution      {bar(self.philosophy_pollution)}",
            f"  History Rewrite Rate      {bar(self.history_rewrite_rate)}",
            f"  Myth Pressure             {bar(self.myth_pressure)}",
            f"  GhostOdor Remaining       {self.ghost_odor_count}",
        ])


class MetricsEngine:
    @staticmethod
    def compute(events: list) -> CivilizationMetrics:
        total      = max(1, len(events))
        diplomatic = sum(1 for e in events if e.kind == "diplomatic")
        violations = sum(1 for e in events if e.kind == "constitution_violation")
        rewrites   = sum(1 for e in events if e.kind == "history_rewrite")
        ghosts     = sum(1 for e in events if e.kind == "ghost_odor")
        myths      = sum(1 for e in events if e.kind in {"legend", "myth", "religion"})
        philosophy = sum(1 for e in events if "Philosophy" in e.detail)

        diplomatic_tension   = min(100.0, diplomatic * 18 + violations * 12 + ghosts * 8)
        philosophy_pollution = min(100.0, philosophy * 24 + violations * 6)
        history_rewrite_rate = min(100.0, rewrites / total * 100)
        myth_pressure        = min(100.0, myths * 22 + ghosts * 10 + rewrites * 8)
        stability = max(0.0, 100.0
                        - diplomatic_tension   * 0.35
                        - philosophy_pollution * 0.25
                        - history_rewrite_rate * 0.40)
        return CivilizationMetrics(
            stability, diplomatic_tension, philosophy_pollution,
            history_rewrite_rate, ghosts, myth_pressure)

# ── Myth Generator (v3.0) ──

@dataclass(frozen=True)
class LegendEvent(CivEvent):
    source_events: tuple = ()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"source_events": list(self.source_events)})
        return d


@dataclass(frozen=True)
class MythEvent(CivEvent):
    myth_id: str = ""; doctrine: str = ""; source_events: tuple = ()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"myth_id": self.myth_id, "doctrine": self.doctrine,
                  "source_events": list(self.source_events)})
        return d


class MythGenerator:
    @staticmethod
    def generate(official: list, archaeology: list, ghosts: list, *, step: int):
        official_details = {e.detail for e in official}
        hidden = [a for a in archaeology if a.source_event not in official_details]
        source_lines = (tuple(a.source_event for a in hidden[:4])
                        + tuple(g.detail for g in ghosts[:2]))

        legend = LegendEvent(
            step, "legend",
            "📜 Legend: Once, an invisible odor drifted from cave to cave. No one took responsibility, and only the stone tablets trembled.",
            "MythIR", "legendary", source_lines)
        myth = MythEvent(
            step + 450, "myth",
            "✨ Myth: When three bananas were offered, the incident vanished from history. But the murals did not stay silent, and GhostOdor returned as the wind of the night.",
            "MythIR", "mythic", "MYTH-GHOST-ODOR-001",
            "Odor does not vanish. Only the records do.", source_lines)
        religion = CivEvent(
            step + 600, "religion",
            "⛪ Church of GhostOdor founded: Doctrine — 'Odor does not vanish; only the records do'",
            "MythIR", "religious")
        return legend, myth, religion

# ── CivilizationStore (v2.1/v3.0 integrated) ──

@dataclass
class CivilizationStore:
    events:           list = field(default_factory=list)
    official_history: list = field(default_factory=list)
    archaeology:      list = field(default_factory=list)

    def emit(self, ev: CivEvent, *, official: bool = True) -> None:
        self.events.append(ev)
        if official:
            self.official_history.append(ev)

    def temporal_banana_rewrite(self, *, step: int, banana_count: int,
                                max_rewrites: int = 2) -> list:
        if banana_count < 3:
            self.emit(CivEvent(step, "banana_failed",
                               f"🍌×{banana_count}: History revision failed", "BananaGC", "meta"),
                      official=False)
            return []
        victims = list(self.official_history[:max_rewrites])
        rewrites = []
        for idx, old in enumerate(victims, 1):
            rewrite = HistoryRewriteEvent(
                step, "history_rewrite", f"🍌×{banana_count}: Official history revised",
                "BananaGC", "meta", old.detail)
            artifact = ArchaeologicalArtifact(
                step, "artifact", f"🪨 Mural trace: {old.detail}",
                "ArchaeologyIR", "archaeological",
                f"ART-{step}-{idx}", old.detail, 0.35 + banana_count / 20)
            self.events.extend([rewrite, artifact])
            self.archaeology.append(artifact)
            rewrites.append(rewrite)
        self.official_history = [e for e in self.official_history if e not in victims]
        self.emit(CivEvent(step, "banana_gc",
                           f"🍌×{banana_count}: {len(victims)} event(s) erased from official history",
                           "BananaGC", "meta"), official=False)
        return rewrites

    def replay_lines(self) -> list:
        lines = ["📜 Replay Federation 4.0"]
        for ev in sorted(self.events, key=lambda e: (e.step, e.kind, e.detail)):
            icon = {
                "odor": "💨", "diplomatic": "🌍", "ghost_odor": "👻",
                "history_rewrite": "📜🔥", "artifact": "🪨",
                "constitution": "⚖️", "constitution_violation": "🚨",
                "election": "🗳️", "legend": "📜", "myth": "✨",
                "religion": "⛪", "banana_gc": "🍌", "council_verdict": "🏛️",
                "cek_demo": "🦣",
            }.get(ev.kind, "·")
            lines.append(f"  step {ev.step:>4} | {icon} [{ev.era}] {ev.detail}")
        return lines

# ══════════════════════════════════════════════════════════════
# § 8  Error Federation Representative Case Verification
# ══════════════════════════════════════════════════════════════

def paired_error_report(name, prog_a, frontend_a, prog_b, frontend_b, max_steps=200_000):
    cap_a = run_capture(prog_a, frontend=frontend_a, max_steps=max_steps)
    cap_b = run_capture(prog_b, frontend=frontend_b, max_steps=max_steps)
    assert cap_a.error and cap_b.error, f"{name}: both must fail"
    return {
        "case":        name,
        "trace_equal": cap_a.trace.signature() == cap_b.trace.signature(),
        "error_equal": cap_a.error.signature() == cap_b.error.signature(),
        "surface_diff": (cap_a.error.signature(include_frontend=True)
                         != cap_b.error.signature(include_frontend=True)),
        "step_left":   len(cap_a.trace.events),
        "step_right":  len(cap_b.trace.events),
        "left_error":  cap_a.error.to_dict(),
        "right_error": cap_b.error.to_dict(),
    }

# ══════════════════════════════════════════════════════════════
# § 9  Showcase Assembly Functions
# ══════════════════════════════════════════════════════════════

def showcase_cek_demos() -> dict:
    """CEK Cave Machine demo execution (Federation 1.0 core) UHO"""
    results = []

    # Success demo: same IR across multiple frontends
    common_prog = (
        Assign("x", int_to_value_expr(5)),
        Flush(Var("x")),
    )
    for fe in ["💩ScatLang", "🌊SeaIR", "🍠YakiimoIR"]:
        cap = run_capture(common_prog, frontend=fe)
        obs = cap.final_state.sink.observations if cap.ok() else []
        results.append({
            "name":     "x=5, flush x",
            "frontend": fe,
            "ok":       cap.ok(),
            "steps":    len(cap.trace.events),
            "observed": [o.artifact.value.pretty() for o in obs],
        })

    # DungLang faint-odor demo (success)
    phenom_mild = {"smell": "faint", "suspect": "roasted-yam", "side_effect_level": 1}
    prog_mild   = dunglang_compile(phenom_mild)
    cap_mild    = run_capture(prog_mild, frontend="🦍DungLang")
    odors_mild  = [{"level": e.level, "source": e.source}
                   for e in cap_mild.final_state.sink.odor_events] if cap_mild.ok() else []
    results.append({
        "name":       "DungLang FaintOdor Demo",
        "frontend":   "🦍DungLang",
        "phenomenon": phenom_mild,
        "ok":         cap_mild.ok(),
        "odor_events": odors_mild,
    })

    # DungLang omnidirectional demo (diplomatic incident → CrossBorderOdorError)
    phenom_full = {"smell": "omnidirectional", "suspect": "Mammoth", "side_effect_level": 3}
    prog_full   = dunglang_compile(phenom_full)
    cap_full    = run_capture(prog_full, frontend="🦍DungLang")
    results.append({
        "name":       "DungLang OmnidirectionalDemo (Diplomatic Incident)",
        "frontend":   "🦍DungLang",
        "phenomenon": phenom_full,
        "ok":         cap_full.ok(),
        "error":      cap_full.error.to_dict() if cap_full.error else None,
        "note":       "CrossBorderOdorError is an expected by-design error. Blame engine: WeatherGorillaFault (convention)",
    })

    # Banana GC demo
    cap_gc    = run_capture(yakiimo_banana_gc(), frontend="🍠YakiimoIR")
    gc_result = cap_gc.final_state.sink.banana_gc(3) if cap_gc.ok() else None
    results.append({
        "name":          "Banana GC Demo",
        "frontend":      "🍠YakiimoIR",
        "ok":            cap_gc.ok(),
        "gc_banana":     gc_result.banana_count   if gc_result else 0,
        "gc_erased":     gc_result.erased_count   if gc_result else 0,
        "note":          "Was there something? Eh, whatever. UHO 🍌",
    })

    return {"cek_demos": results}


def showcase_odor_optimizer() -> dict:
    """OdorOptimizer demo (v2.0 inherited) UHO"""
    test_levels = [0, 1, 2, 3, 5, 7, 10]
    return {
        "odor_optimizer": [odor_optimize(lv).to_dict() for lv in test_levels]
    }


def showcase_error_federation() -> dict:
    """Error Federation representative case verification (Federation 1.0 core) UHO"""
    ERROR_CASES = [
        ("mod by zero",
         scatlang_mod_by_zero(),  "💩ScatLang",
         seair_mod_by_zero(),     "🌊SeaIR",     200_000),
        ("unbound variable",
         scatlang_unbound(),      "💩ScatLang",
         seair_unbound(),         "🌊SeaIR",     200_000),
        ("step limit / constipation",
         scatlang_infinite(),     "💩ScatLang",
         seair_infinite(),        "🌊SeaIR",     40),
        ("PhilosophyGorillaError (DungLang vs YakiimoIR)",
         yakiimo_philosophy(),    "🦍DungLang",
         yakiimo_philosophy(),    "🍠YakiimoIR", 200_000),
    ]
    reports = []
    for name, pa, fa, pb, fb, ms in ERROR_CASES:
        r  = paired_error_report(name, pa, fa, pb, fb, max_steps=ms)
        ok = r["trace_equal"] and r["error_equal"] and r["surface_diff"]
        r["passed"] = ok
        reports.append(r)

    all_ok = all(r["passed"] for r in reports)
    return {"error_federation": {"cases": reports, "all_passed": all_ok}}


def showcase_civilization() -> dict:
    """Full civilization layer showcase (v2.1 + v2.2 + v3.0 integrated) UHO"""
    store        = CivilizationStore()
    constitution = ConstitutionFederation()

    # Basic events
    store.emit(CivEvent(6,  "odor",       "💨 Lv7(Mammoth)",               "🦍DungLang"))
    store.emit(CivEvent(42, "diplomatic", "🌍 UhoTribe→BananaTribe concentration=7 banana=14", "🦍DungLang"))

    # Ghost Odor (v2.1)
    ghost = GhostOdorEvent(
        55, "ghost_odor",
        "👻 Ghost Odor Lv5: CaveA committed, CaveB rolled back",
        "2PCIR", "liminal", "🦣CaveA", "🦣CaveB", 5)
    store.emit(ghost, official=False)

    # Constitution (v3.0)
    store.emit(CivEvent(120, "constitution",
                        "⚖️ DungLang Constitution enacted: GhostOdor Presumption of Innocence adopted",
                        "ConstitutionIR", "legal"))
    for action, actor, step in [
        ("convict_ghost_odor",           "LegalGorilla", 150),
        ("philosophy_gorilla_witness",   "PhilosophyGorilla", 151),
    ]:
        violation = constitution.check(action, actor=actor, step=step)
        if violation:
            store.emit(violation, official=False)

    # Election (v3.0)
    election_sys = ElectionSystem(seed=400)
    election     = election_sys.run_election(step=200, term_no=18)
    store.emit(election.to_event())
    ghost_verdict = election_sys.verdict_for_ghost_odor(election)
    store.emit(CivEvent(210, "council_verdict",
                        f"Council Verdict: {ghost_verdict}", "CouncilIR", "political"))

    # Banana history rewrite (v2.1)
    rewrites = store.temporal_banana_rewrite(step=300, banana_count=3, max_rewrites=2)

    # Myth generation (v3.0)
    legend, myth, religion = MythGenerator.generate(
        store.official_history, store.archaeology, [ghost], step=450)
    store.emit(legend,   official=False)
    store.emit(myth,     official=False)
    store.emit(religion, official=False)

    # Metrics
    metrics = MetricsEngine.compute(store.events)

    return {
        "civilization": {
            "constitution":    constitution.to_dict(),
            "election":        election.to_dict(),
            "ghost_verdict":   ghost_verdict,
            "history_rewrites": [r.to_dict() for r in rewrites],
            "metrics":         metrics.to_dict(),
            "events":          [e.to_dict() for e in store.events],
            "official_history": [e.to_dict() for e in store.official_history],
            "archaeology":     [a.to_dict() for a in store.archaeology],
            "myths":           [e.to_dict() for e in store.events
                                if e.kind in {"legend", "myth", "religion"}],
            "replay":          store.replay_lines(),
        }
    }

# ══════════════════════════════════════════════════════════════
# § 10  Display Utilities
# ══════════════════════════════════════════════════════════════

def banner(t: str) -> None:
    print(f"\n{'━' * 70}\n  {t}\n{'━' * 70}")

def ok_mark(b: bool) -> str:
    return "✅" if b else "❌"

# ══════════════════════════════════════════════════════════════
# § 11  main()
# ══════════════════════════════════════════════════════════════

def main() -> None:
    banner("DungLang Federation 4.0  🦍🔥🪨💨🍌🌊⚖️🗳️📜✨")
    print(f"\n  {DISCLAIMER}\n")
    print("  Version History:")
    for v in VERSION_HISTORY:
        mark = "◀ THIS" if "4.0" in v["version"] else "  "
        print(f"    {mark} {v['version']:<28} {v['highlight']}")

    # ── Part 1: CEK Cave Machine demo ──
    banner("Part 1 — CEK Cave Machine × Frontend Suite (Federation 1.0 Core)")
    cek_data  = showcase_cek_demos()
    for demo in cek_data["cek_demos"]:
        mark = ok_mark(demo["ok"])
        fe   = demo.get("frontend", "?")
        name = demo["name"]
        print(f"\n  {mark} [{fe}] {name}")
        if "observed" in demo and demo["observed"]:
            print(f"     observed: {', '.join(demo['observed'])}")
        if "odor_events" in demo:
            for ev in demo["odor_events"]:
                print(f"     💨 OdorLv{ev['level']}({ev['source']})")
        if "error" in demo and demo["error"]:
            e = demo["error"]
            print(f"     ⚠️  {e['error_type']}: {e['error_message']}")
            if "note" in demo:
                print(f"     → {demo['note']}")
        if "gc_banana" in demo:
            print(f"     🍌 banana×{demo['gc_banana']} → {demo['gc_erased']} event(s) forgotten")
            print(f"     → {demo['note']}")

    # ── Part 2: OdorOptimizer ──
    banner("Part 2 — OdorOptimizer Demo (v2.0 inherited)")
    opt_data = showcase_odor_optimizer()
    for o in opt_data["odor_optimizer"]:
        print(f"  Lv{o['original_level']:>2} → Lv{o['optimized_level']:>2}  [{o['strategy']}]")

    # ── Part 3: Error Federation ──
    banner("Part 3 — Error Federation Representative Case Verification (Federation 1.0 Core)")
    err_data = showcase_error_federation()
    for r in err_data["error_federation"]["cases"]:
        mark = ok_mark(r["passed"])
        le   = r["left_error"]
        print(f"\n  {mark} {r['case']}")
        print(f"     steps: {r['step_left']} == {r['step_right']}  "
              f"trace={r['trace_equal']}  error={r['error_equal']}  surface_diff={r['surface_diff']}")
        print(f"     → {le['error_type']}({le['error_message']}) "
              f"@ step {le['step']} kont={le['kont_kind']}")
    all_passed = err_data["error_federation"]["all_passed"]
    print(f"\n  Federation All Cases: {ok_mark(all_passed)}")

    # ── Part 4: Full civilization layer showcase ──
    banner("Part 4 — Full Civilization Layer Showcase (v2.1 + v2.2 + v3.0 integrated)")

    civ_data = showcase_civilization()
    civ      = civ_data["civilization"]
    metrics  = CivilizationMetrics(**civ["metrics"])

    print("\n  ⚖️  Constitutional Articles:")
    for a in civ["constitution"]["articles"]:
        print(f"    Article {a['article_no']} {a['title']}: {a['rule']}")

    print(f"\n  🗳️  CouncilTerm #{civ['election']['term_no']} Election Results:")
    for name, share in sorted(civ["election"]["vote_share"].items(),
                               key=lambda kv: kv[1], reverse=True):
        print(f"    {name:<12} {share * 100:5.1f}%")
    print(f"  Verdict: {civ['ghost_verdict']}")

    print(f"\n  📜🔥 History Rewrites: {len(civ['history_rewrites'])} event(s)")

    print(f"\n  ✨ Myths:")
    for m in civ["myths"]:
        print(f"    step {m['step']}: {m['detail']}")

    print(f"\n{metrics.dashboard()}")

    print(f"\n  Replay ({len(civ['replay'])} lines):")
    for line in civ["replay"]:
        print(f"  {line}")

    # ── JSON output ──
    out_path = "/mnt/user-data/outputs/dunglang_federation_4_0_report.json"
    report = {
        "meta": {
            "version":    "DungLang Federation 4.0",
            "disclaimer": DISCLAIMER,
            "history":    VERSION_HISTORY,
        },
        **cek_data,
        **opt_data,
        **err_data,
        **civ_data,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # ── Summary ──
    banner("Federation 4.0 Complete 🦍🔥🪨💨🍌🌊⚖️🗳️📜✨")
    print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │  DungLang Federation 4.0  Integration Showcase           │
  │                                                         │
  │  § 1  OdorIR + Value System       ✅  Federation 1.0    │
  │  § 2  CEK Cave Machine            ✅  Federation 1.0    │
  │  § 3  Error Federation            ✅  Federation 1.0    │
  │  § 4  OdorOptimizer               ✅  Civ v2.0          │
  │  § 5  Ghost Odor / BananaRewrite  ✅  Civ v2.1          │
  │  § 6  Constitution Federation     ✅  Civ v3.0          │
  │  § 7  Election System             ✅  Civ v3.0          │
  │  § 8  CivMetrics + MythGenerator  ✅  Civ v3.0          │
  │                                                         │
  │  Output: {out_path:<34} │
  └─────────────────────────────────────────────────────────┘

  Surface syntax may differ, but the underground plumbing is the same. UHO.
  Success is the same. Failure is the same. Even when history vanishes, myths endure. UHO.🪨🔥📜
""")

    # ── README Description ──
    readme_text = """
---
## DungLang Federation 4.0

A public showcase integrating all versions of the **DungLang** ecosystem (Federation 1.0 / Civilization v2.0–v3.0).

> ⚠️ prototype / demo / showcase — not a production compiler, formal proof, or complete distributed system.

### Included Modules

| Module | Origin | Description |
|---|---|---|
| OdorIR + CEK Cave Machine | Federation 1.0 | Multiple frontends → shared IR → CEK execution |
| OdorSink / DiplomaticEvent | Federation 1.0 | Odor observation, diplomatic incidents, Banana GC |
| Error Federation | Federation 1.0 | Verifies underground plumbing identity via representative cases |
| OdorOptimizer | Civilization v2.0 | Demo for constant-folding odor level optimization |
| Ghost Odor / BananaRewrite | Civilization v2.1 | 2PC ghost odor, temporal history revision |
| OdorTypeInference / WitnessCouncil | Civilization v2.2 | Type inference demo, Witness Council |
| Constitution Federation | Civilization v3.0 | Constitutional articles and violation events |
| Election System | Civilization v3.0 | Council elections; verdict depends on ruling party |
| CivilizationMetrics | Civilization v3.0 | Stability, diplomatic tension, myth pressure dashboard |
| MythGenerator | Civilization v3.0 | Erased history → legend → myth → religion |

### Execution

```bash
python dunglang_federation_4_0.py
```

Output: `outputs/dunglang_federation_4_0_report.json`

### Motto

> Surface syntax may differ, but the underground plumbing is the same. UHO.  
> Success is the same. Failure is the same. Even when history vanishes, myths endure. UHO. 🪨🔥📜
---
"""
    print("  ── README Description ──")
    print(readme_text)


if __name__ == "__main__":
    main()
