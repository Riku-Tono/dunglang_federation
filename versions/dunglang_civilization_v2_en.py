# -*- coding: utf-8 -*-
"""
DungLang Civilization v2.0
===========================
  ① OdorIR Optimizer       (OdorOptimizer)
  ② Kont Federation        (Continuation tree identity proof)
  ③ History Federation     (HistoryRewriteEvent — history gets rewritten)
  ④ Mammoth Distributed Transaction (Ghost Odor)
  ⑥ Gorilla Incompleteness Theorem (neither can be proved)
  ★ Replay Civilization    (civilization event-sourcing replay)

  DungLang = worldview
  MysticIR = verification engine
  Federation = civilization simulator   🦍🔥🍌💨🌍📜
"""
from __future__ import annotations
import json, re, sys, random, copy
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# ══════════════════════════════════════════════════════════════
# § 0  Foundation (inherited from Federation 1.0 — minimal version)
# ══════════════════════════════════════════════════════════════

class ScatError(Exception): pass
class StepLimitError(ScatError): pass
class PhilosophyGorillaError(ScatError): pass
class AxiomDestructionError(ScatError): pass
class CrossBorderOdorError(ScatError): pass
class GhostOdorError(ScatError): pass   # ④ new

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

def int_to_poop(n):
    v: Value = PoopZero()
    for _ in range(n): v = PoopSucc(v)
    return v

TRUE  = PoopSucc(PoopZero())
FALSE = PoopZero()

# OdorIR expressions and statements
class Expr: pass
class Stmt: pass

@dataclass(frozen=True)
class PoopZeroExpr(Expr): pass
@dataclass(frozen=True)
class PoopSuccExpr(Expr): expr: Expr
@dataclass(frozen=True)
class Var(Expr): name: str
@dataclass(frozen=True)
class OdorAdd(Expr): left: Expr; right: Expr
@dataclass(frozen=True)
class OdorNeq(Expr): left: Expr; right: Expr
@dataclass(frozen=True)
class OdorMod(Expr): left: Expr; right: Expr
@dataclass(frozen=True)
class OdorEq(Expr):  left: Expr; right: Expr
@dataclass(frozen=True)
class OdorSub(Expr): left: Expr; right: Expr
@dataclass(frozen=True)
class OdorPred(Expr): expr: Expr
@dataclass(frozen=True)
class PhilosophyExpr(Expr): question: str
@dataclass(frozen=True)
class OdorLevelExpr(Expr):
    """① Constant-folded odor level after optimization"""
    level: int

@dataclass(frozen=True)
class Assign(Stmt): name: str; expr: Expr
@dataclass(frozen=True)
class Flush(Stmt):  expr: Expr
@dataclass(frozen=True)
class OdorFlush(Stmt): expr: Expr; source: str = "unknown"
@dataclass(frozen=True)
class DiplomaticFlush(Stmt): expr: Expr; from_tribe: str; to_tribe: str
@dataclass(frozen=True)
class While(Stmt): left: Expr; right: Expr; body: tuple

def int_to_expr(n):
    e = PoopZeroExpr()
    for _ in range(n): e = PoopSuccExpr(e)
    return e

def expr_to_int(e) -> Optional[int]:
    """For constant folding. UHO"""
    if isinstance(e, PoopZeroExpr): return 0
    if isinstance(e, PoopSuccExpr):
        inner = expr_to_int(e.expr)
        return None if inner is None else inner + 1
    if isinstance(e, OdorLevelExpr): return e.level
    return None

# Kont and State (no abbreviations)
class Kont: pass
@dataclass(frozen=True)
class Halt(Kont): pass
@dataclass(frozen=True)
class AssignK(Kont): name: str; rest: tuple; env: Any; kont: Kont
@dataclass(frozen=True)
class FlushK(Kont):  rest: tuple; env: Any; kont: Kont
@dataclass(frozen=True)
class OdorFlushK(Kont): rest: tuple; env: Any; kont: Kont; source: str
@dataclass(frozen=True)
class DiplomaticFlushK(Kont): rest: tuple; env: Any; kont: Kont; from_tribe: str; to_tribe: str
@dataclass(frozen=True)
class SuccK(Kont): kont: Kont
@dataclass(frozen=True)
class AddLeftK(Kont):  right: Expr; env: Any; kont: Kont
@dataclass(frozen=True)
class AddRightK(Kont): left_val: Value; kont: Kont
@dataclass(frozen=True)
class NeqLeftK(Kont):  right: Expr; env: Any; kont: Kont
@dataclass(frozen=True)
class NeqRightK(Kont): left_val: Value; kont: Kont
@dataclass(frozen=True)
class SubLeftK(Kont):  right: Expr; env: Any; kont: Kont
@dataclass(frozen=True)
class SubRightK(Kont): left_val: Value; kont: Kont
@dataclass(frozen=True)
class ModLeftK(Kont):  right: Expr; env: Any; kont: Kont
@dataclass(frozen=True)
class ModRightK(Kont): left_val: Value; kont: Kont
@dataclass(frozen=True)
class EqLeftK(Kont):   right: Expr; env: Any; kont: Kont
@dataclass(frozen=True)
class EqRightK(Kont):  left_val: Value; kont: Kont
@dataclass(frozen=True)
class WhileK(Kont): stmt: While; rest: tuple; env: Any; kont: Kont
@dataclass(frozen=True)
class EvalExpr:    expr: Expr
@dataclass(frozen=True)
class ReturnValue: value: Value

# ══════════════════════════════════════════════════════════════
# § 1  OdorIR Optimizer UHO 🔥
#       OdorAdd/PoopSucc chains → folded into OdorLevelExpr(n)
#       Philosophy chains → axiom destruction probability pre-computed
# ══════════════════════════════════════════════════════════════

@dataclass
class OptimizeReport:
    original_nodes: int
    optimized_nodes: int
    folded_odor: int          # number of odor nodes folded
    philosophy_calls: int     # number of philosophy calls
    axiom_break_prob: float   # axiom destruction probability (%)

def count_nodes(e) -> int:
    if isinstance(e, (PoopZeroExpr, OdorLevelExpr, Var, PhilosophyExpr)): return 1
    if isinstance(e, PoopSuccExpr): return 1 + count_nodes(e.expr)
    if isinstance(e, (OdorAdd, OdorNeq, OdorMod, OdorEq, OdorSub)):
        return 1 + count_nodes(e.left) + count_nodes(e.right)
    if isinstance(e, OdorPred): return 1 + count_nodes(e.expr)
    return 1

def optimize_expr(e: Expr) -> Expr:
    """Constant folding + identity transformation elimination. UHO"""
    # PoopSucc chain → OdorLevelExpr
    v = expr_to_int(e)
    if v is not None:
        return OdorLevelExpr(v)
    # OdorAdd with both sides constant
    if isinstance(e, OdorAdd):
        l, r = optimize_expr(e.left), optimize_expr(e.right)
        lv, rv = expr_to_int(l), expr_to_int(r)
        if lv is not None and rv is not None:
            return OdorLevelExpr(lv + rv)
        return OdorAdd(l, r)
    if isinstance(e, OdorSub):
        l, r = optimize_expr(e.left), optimize_expr(e.right)
        lv, rv = expr_to_int(l), expr_to_int(r)
        if lv is not None and rv is not None:
            return OdorLevelExpr(max(lv - rv, 0))
        return OdorSub(l, r)
    if isinstance(e, OdorMod):
        l, r = optimize_expr(e.left), optimize_expr(e.right)
        lv, rv = expr_to_int(l), expr_to_int(r)
        if lv is not None and rv is not None and rv != 0:
            return OdorLevelExpr(lv % rv)
        return OdorMod(l, r)
    if isinstance(e, OdorNeq):
        l, r = optimize_expr(e.left), optimize_expr(e.right)
        return OdorNeq(l, r)
    if isinstance(e, PoopSuccExpr):
        inner = optimize_expr(e.expr)
        iv = expr_to_int(inner)
        if iv is not None: return OdorLevelExpr(iv + 1)
        return PoopSuccExpr(inner)
    return e

def count_philosophy(prog: tuple) -> int:
    n = 0
    for s in prog:
        if isinstance(s, Assign) and isinstance(s.expr, PhilosophyExpr): n += 1
        if isinstance(s, Flush)  and isinstance(s.expr, PhilosophyExpr): n += 1
    return n

def optimize_program(prog: tuple) -> tuple[tuple, OptimizeReport]:
    orig_nodes = sum(count_nodes(s.expr) for s in prog
                     if hasattr(s, 'expr'))
    optimized = []
    for s in prog:
        if isinstance(s, Assign):
            optimized.append(Assign(s.name, optimize_expr(s.expr)))
        elif isinstance(s, (Flush, OdorFlush)):
            cls = type(s)
            kw = {}
            if isinstance(s, OdorFlush): kw['source'] = s.source
            optimized.append(cls(optimize_expr(s.expr), **kw))
        elif isinstance(s, DiplomaticFlush):
            optimized.append(DiplomaticFlush(optimize_expr(s.expr),
                                              s.from_tribe, s.to_tribe))
        else:
            optimized.append(s)
    opt_nodes = sum(count_nodes(s.expr) for s in optimized
                    if hasattr(s, 'expr'))
    phil_calls = count_philosophy(tuple(optimized))
    # PhilosophyGorilla axiom destruction probability: low for 1, spikes at 3+
    prob = min(97.0, phil_calls * 32.3)
    report = OptimizeReport(
        original_nodes=orig_nodes, optimized_nodes=opt_nodes,
        folded_odor=orig_nodes - opt_nodes,
        philosophy_calls=phil_calls, axiom_break_prob=prob,
    )
    return tuple(optimized), report

# ══════════════════════════════════════════════════════════════
# § 2  Kont Tree — ② Kont Federation
#       Records and compares continuation stacks as trees. UHO
# ══════════════════════════════════════════════════════════════

@dataclass
class KontTree:
    kind: str
    children: list = field(default_factory=list)
    meta: str = ""

    def signature(self) -> tuple:
        return (self.kind, self.meta,
                tuple(c.signature() for c in self.children))

    def pretty(self, indent=0) -> str:
        pad = "  " * indent
        s = f"{pad}{self.kind}"
        if self.meta: s += f"({self.meta})"
        for c in self.children:
            s += "\n" + c.pretty(indent + 1)
        return s

def kont_to_tree(k: Kont) -> KontTree:
    if isinstance(k, Halt):
        return KontTree("Halt")
    meta = ""
    if hasattr(k, 'name'):  meta = k.name
    if hasattr(k, 'source'): meta = k.source
    child = kont_to_tree(getattr(k, 'kont', Halt()))
    return KontTree(type(k).__name__, [child], meta)

@dataclass(frozen=True)
class KontSnapshot:
    step: int
    tree: KontTree
    frontend: str

    def signature(self):
        return (self.step, self.tree.signature())

# ══════════════════════════════════════════════════════════════
# § 3  Civilization Event Groups — ③ History Federation + ★ Replay
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CivEvent:
    step: int; kind: str; detail: str; frontend: str

    def to_dict(self):
        return dict(step=self.step, kind=self.kind,
                    detail=self.detail, frontend=self.frontend)

@dataclass(frozen=True)
class HistoryRewriteEvent(CivEvent):
    """③ History has been rewritten. UHO"""
    erased_event: str = ""
    rewritten_as: str = "deemed to have never existed from the start"

    def to_dict(self):
        d = super().to_dict()
        d.update(erased_event=self.erased_event,
                 rewritten_as=self.rewritten_as)
        return d

@dataclass(frozen=True)
class GhostOdorEvent(CivEvent):
    """④ Ghost Odor — odor exists, no culprit"""
    cave_a: str = ""; cave_b: str = ""
    odor_level: int = 0

    def to_dict(self):
        d = super().to_dict()
        d.update(cave_a=self.cave_a, cave_b=self.cave_b,
                 odor_level=self.odor_level)
        return d

# ══════════════════════════════════════════════════════════════
# § 4  CivilizationSink — OdorSink complete form
#       Saves all events using event-sourcing. UHO
# ══════════════════════════════════════════════════════════════

TREATY = {
    ("UhoTribe","BananaTribe"): 3,
    ("UhoTribe","MammothTribe"): 5,
    ("BananaTribe","MammothTribe"): 4,
}

@dataclass
class CivilizationSink:
    frontend: str = "unknown"
    step_count: int = 0
    _events: list = field(default_factory=list)           # full event timeline
    _observations: list = field(default_factory=list)
    _kont_snapshots: list = field(default_factory=list)   # ② Kont tree snapshots
    _erased_events: list = field(default_factory=list)    # ③ erased events
    _history: list = field(default_factory=list)          # official history (post-rewrite)

    def tick(self): self.step_count += 1

    def _emit(self, ev: CivEvent):
        self._events.append(ev)
        self._history.append(ev)

    def observe(self, v: Value, ctx: str = "flush"):
        self._observations.append((v, self.step_count, ctx))
        self._emit(CivEvent(self.step_count, "observe",
                            f"{v.pretty()}", self.frontend))

    def observe_odor(self, level: int, source: str, ctx: str = "odor"):
        ev = CivEvent(self.step_count, "odor",
                      f"💨 Lv{level}({source})", self.frontend)
        self._emit(ev)

    def observe_diplomatic(self, level: int, ft: str, tt: str):
        treaty = TREATY.get((ft, tt), 4)
        if level > treaty:
            verdict, banana = "DiplomaticIncident", level * 2
            ev = CivEvent(self.step_count, "diplomatic",
                          f"🌍 {ft}→{tt} concentration={level} banana={banana}", self.frontend)
            self._emit(ev)
            raise CrossBorderOdorError(f"{ft}→{tt} concentration={level} banana_reparations={banana}")
        else:
            ev = CivEvent(self.step_count, "diplomatic",
                          f"🌤️ WeatherGorillaFault({ft}→{tt})", self.frontend)
            self._emit(ev)

    def banana_gc(self, n: int):
        erased_count = len(self._history)
        # ③ HistoryRewriteEvent: record erased events
        for old_ev in list(self._history):
            hrev = HistoryRewriteEvent(
                step=self.step_count, kind="history_rewrite",
                detail=f"🍌×{n} history revision", frontend=self.frontend,
                erased_event=old_ev.detail,
                rewritten_as="deemed to have never existed from the start",
            )
            self._erased_events.append(hrev)
        self._history.clear()
        ev = CivEvent(self.step_count, "banana_gc",
                      f"🍌×{n} → {erased_count} event(s) erased from history", self.frontend)
        self._events.append(ev)  # GC itself is not erased (meta-history)
        return erased_count

    def snapshot_kont(self, step_no: int, k: Kont):
        """② Kont tree snapshot"""
        self._kont_snapshots.append(KontSnapshot(step_no, kont_to_tree(k), self.frontend))

    @property
    def observations(self): return tuple(self._observations)
    @property
    def events(self): return list(self._events)
    @property
    def kont_snapshots(self): return list(self._kont_snapshots)
    @property
    def erased_events(self): return list(self._erased_events)
    @property
    def live_history(self): return list(self._history)

# ══════════════════════════════════════════════════════════════
# § 5  CEK Cave Machine (CivilizationSink compatible)
# ══════════════════════════════════════════════════════════════

@dataclass
class State:
    control: object; env: dict; kont: Kont; sink: CivilizationSink

def is_halted(s): return isinstance(s.control, ReturnValue) and isinstance(s.kont, Halt)

def poop_add(a, b): return int_to_poop(a.to_int() + b.to_int())
def poop_sub(a, b): return int_to_poop(max(a.to_int() - b.to_int(), 0))
def poop_pred(v):
    if isinstance(v, PoopZero): return Underflow()
    if isinstance(v, PoopSucc): return v.inner
    return Underflow()
def poop_mod(a, b):
    if b.to_int() == 0: raise ScatError("mod by zero")
    return int_to_poop(a.to_int() % b.to_int())
def poop_neq(a, b): return TRUE if a.to_int() != b.to_int() else FALSE
def poop_eq(a, b):  return TRUE if a.to_int() == b.to_int()  else FALSE

def step(state: State) -> State:
    state.sink.tick()
    ctrl = state.control

    if isinstance(ctrl, tuple):
        if not ctrl:
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)
        head, *tail = ctrl; rest = tuple(tail)
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
        if isinstance(e, (PoopZeroExpr,)):
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)
        if isinstance(e, OdorLevelExpr):          # ① optimized direct value
            return State(ReturnValue(int_to_poop(e.level)), state.env, state.kont, state.sink)
        if isinstance(e, PoopSuccExpr):
            return State(EvalExpr(e.expr), state.env, SuccK(state.kont), state.sink)
        if isinstance(e, Var):
            if e.name not in state.env: raise ScatError(f"unbound variable: {e.name}")
            return State(ReturnValue(state.env[e.name]), state.env, state.kont, state.sink)
        if isinstance(e, OdorAdd):
            return State(EvalExpr(e.left), state.env,
                         AddLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorNeq):
            return State(EvalExpr(e.left), state.env,
                         NeqLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorSub):
            return State(EvalExpr(e.left), state.env,
                         SubLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorMod):
            return State(EvalExpr(e.left), state.env,
                         ModLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorEq):
            return State(EvalExpr(e.left), state.env,
                         EqLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorPred):
            return State(EvalExpr(e.expr), state.env, OdorFlushK((), {}, state.kont, "pred"), state.sink)
        if isinstance(e, PhilosophyExpr):
            raise PhilosophyGorillaError(e.question)
        raise ScatError(f"unknown expr: {e!r}")

    if isinstance(ctrl, ReturnValue):
        v, k = ctrl.value, state.kont
        if isinstance(k, Halt): return state
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
            state.sink.observe_diplomatic(v.to_int(), k.from_tribe, k.to_tribe)
            return State(k.rest, dict(k.env), k.kont, state.sink)
        if isinstance(k, AddLeftK):
            return State(EvalExpr(k.right), dict(k.env), AddRightK(v, k.kont), state.sink)
        if isinstance(k, AddRightK):
            return State(ReturnValue(poop_add(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, NeqLeftK):
            return State(EvalExpr(k.right), dict(k.env), NeqRightK(v, k.kont), state.sink)
        if isinstance(k, NeqRightK):
            return State(ReturnValue(poop_neq(k.left_val, v)), state.env, k.kont, state.sink)
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
# § 6  TraceCollector + RunCapture (with Kont tree snapshots)
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TraceEvent:
    step: int; control_kind: str; expr_kind: str
    kont_kind: str; kont_depth: int; env_keys: tuple
    observed_count: int; frontend: str

    def signature(self, *, include_frontend=False):
        r = (self.control_kind, self.expr_kind, self.kont_kind,
             self.kont_depth, self.env_keys, self.observed_count)
        return r + ((self.frontend,) if include_frontend else ())

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

@dataclass
class RunCapture:
    final_state: object; trace: TraceCollector
    error: object; sink: CivilizationSink
    kont_snapshots: list = field(default_factory=list)
    def ok(self): return self.error is None

def kont_depth_fn(k):
    d = 0
    while not isinstance(k, Halt):
        d += 1; k = getattr(k, 'kont', None)
        if k is None: break
    return d

def make_trace(step_no, state):
    ctrl = state.control
    if isinstance(ctrl, tuple):   ck, ek = "StmtSeq", f"len={len(ctrl)}"
    elif isinstance(ctrl, EvalExpr):  ck, ek = "EvalExpr", type(ctrl.expr).__name__
    elif isinstance(ctrl, ReturnValue): ck, ek = "ReturnValue", ctrl.value.pretty()
    else: ck, ek = type(ctrl).__name__, ""
    return TraceEvent(
        step=step_no, control_kind=ck, expr_kind=ek,
        kont_kind=type(state.kont).__name__,
        kont_depth=kont_depth_fn(state.kont),
        env_keys=tuple(sorted(state.env.keys())),
        observed_count=len(state.sink.observations),
        frontend=state.sink.frontend,
    )

def make_error(step_no, state, exc):
    t = make_trace(step_no, state)
    return TraceErrorEvent(
        step=t.step, control_kind=t.control_kind, expr_kind=t.expr_kind,
        kont_kind=t.kont_kind, kont_depth=t.kont_depth, env_keys=t.env_keys,
        observed_count=t.observed_count, frontend=t.frontend,
        error_type=type(exc).__name__, error_message=str(exc),
    )

KONT_SNAP_STEPS = {0, 1, 5, 10, 20}  # ② steps at which to take Kont snapshots

def run_capture(prog, env=None, *, frontend, max_steps=200_000,
                optimize=False):
    col  = TraceCollector()
    sink = CivilizationSink(frontend=frontend)
    prog_to_run = prog

    opt_report = None
    if optimize:
        prog_to_run, opt_report = optimize_program(tuple(prog))

    state = State(tuple(prog_to_run), dict(env or {}), Halt(), sink)
    kont_snaps = []

    for step_no in range(max_steps):
        if is_halted(state):
            return RunCapture(state, col, None, sink, kont_snaps), opt_report
        col(make_trace(step_no, state))
        # ② Kont tree snapshot
        if step_no in KONT_SNAP_STEPS:
            kont_snaps.append(KontSnapshot(step_no, kont_to_tree(state.kont), frontend))
        try:
            state = step(state)
        except ScatError as e:
            return RunCapture(None, col, make_error(step_no, state, e), sink, kont_snaps), opt_report

    exc = StepLimitError(f"step limit exceeded: {max_steps}")
    return RunCapture(None, col, make_error(max_steps, state, exc), sink, kont_snaps), opt_report

# ══════════════════════════════════════════════════════════════
# § 7  ④ Mammoth Distributed Transaction — Ghost Odor
#       CaveA success + CaveB failure → odor exists, no culprit
# ══════════════════════════════════════════════════════════════

def mammoth_distributed_transaction(cave_a_prog, cave_b_prog,
                                    fe_a="🦣CaveA", fe_b="🦣CaveB"):
    """
    Transaction {
        CaveA.emit()     # success
        CaveB.observe()  # failure
    }
    → Ghost Odor: odor exists, no culprit
    """
    # Phase 1: Prepare
    print(f"\n  [2Phase] Prepare...")
    cap_a, _ = run_capture(cave_a_prog, frontend=fe_a)
    cap_b, _ = run_capture(cave_b_prog, frontend=fe_b)

    a_ok = cap_a.ok()
    b_ok = cap_b.ok()
    print(f"  {fe_a}: {'✅ success' if a_ok else '❌ failed'}")
    print(f"  {fe_b}: {'✅ success' if b_ok else '❌ failed'}")

    if a_ok and not b_ok:
        # Ghost Odor detected!
        odor_events = cap_a.sink.events
        odor_level  = sum(1 for e in odor_events if e.kind == "odor")
        ghost = GhostOdorEvent(
            step=cap_b.error.step if cap_b.error else 0,
            kind="ghost_odor",
            detail=f"👻 Ghost Odor Lv{odor_level}: odor exists, no culprit",
            frontend=f"{fe_a}+{fe_b}",
            cave_a=fe_a, cave_b=fe_b, odor_level=odor_level,
        )
        print(f"\n  💀 Ghost Odor detected!")
        print(f"     {ghost.detail}")
        print(f"     cause: {fe_a} emitted but {fe_b} rolled back")
        print(f"     → Odor exists in the world. But no one admits it.")
        return ghost
    elif a_ok and b_ok:
        print(f"\n  ✅ Both caves committed successfully")
        return None
    else:
        print(f"\n  ⚠️  Both caves rolled back (no odor)")
        return None

# ══════════════════════════════════════════════════════════════
# § 8  ⑥ Gorilla Incompleteness Theorem
# ══════════════════════════════════════════════════════════════

class GorillaTheoremProver:
    """
    Prove: fart = wind  → proof failed (reason: observer exists)
    Prove: fart ≠ wind  → proof failed (reason: wind direction unknown)
    → Gorilla Incompleteness Theorem: neither can be proved
    """

    axioms = {
        "flatulence is wind until observed": True,
        "roasted yam does not conceal side effects": True,
        "pure functions do not smell": True,
        "once odor is detected, the world has already been modified": True,
    }

    @classmethod
    def prove(cls, statement: str) -> dict:
        if statement == "fart = wind":
            return {
                "statement": statement,
                "result": "proof failed",
                "reason": "an observer exists (the moment of observation collapses the wind possibility. UHO)",
                "theorem": "Gorilla Incompleteness Theorem Lemma 1",
            }
        elif statement == "fart ≠ wind":
            return {
                "statement": statement,
                "result": "proof failed",
                "reason": "wind direction unknown (WeatherGorilla refused to testify. UHO)",
                "theorem": "Gorilla Incompleteness Theorem Lemma 2",
            }
        elif statement == "fart ∈ {wind, fart}":
            return {
                "statement": statement,
                "result": "proof failed",
                "reason": "the set definition was destroyed by PhilosophyGorilla",
                "theorem": "Gorilla Incompleteness Theorem Lemma 3",
            }
        else:
            return {
                "statement": statement,
                "result": "proof failed",
                "reason": "PhilosophyGorilla ate the question. UHO",
                "theorem": "Gorilla Incompleteness Theorem (general form)",
            }

    @classmethod
    def print_theorem(cls):
        print("""
  ┌─────────────────────────────────────────────────────┐
  │  Gorilla Incompleteness Theorem                     │
  │                                                     │
  │  Corollary 1: fart = wind  is unprovable            │
  │  Corollary 2: fart ≠ wind  is also unprovable       │
  │  Corollary 3: this theorem itself is unprovable     │
  │                                                     │
  │  ∀ proposition P ∈ DungLang :                      │
  │    prove(P) = proof_failed  ∨  prove(¬P) = proof_failed │
  │                                                     │
  │  (with roasted-yam correction: truth rate +12%)     │
  └─────────────────────────────────────────────────────┘""")

# ══════════════════════════════════════════════════════════════
# § 9  ★ Replay Civilization
#       Replays all events in chronological order. UHO 📜
# ══════════════════════════════════════════════════════════════

def replay_civilization(all_events: list):
    print("""
  ══════════════════════════════════════════
   📜 Replay Civilization
   Replaying the full history of civilization. UHO
  ══════════════════════════════════════════""")

    by_step = sorted(all_events, key=lambda e: e.step)
    for ev in by_step:
        if isinstance(ev, HistoryRewriteEvent):
            print(f"  step {ev.step:>4} | 📜🔥 History rewrite")
            print(f"           erased: '{ev.erased_event}'")
            print(f"           → {ev.rewritten_as}")
        elif isinstance(ev, GhostOdorEvent):
            print(f"  step {ev.step:>4} | 👻 Ghost Odor Lv{ev.odor_level}")
            print(f"           {ev.cave_a}→{ev.cave_b}: odor alone remains in the world")
        else:
            icon = {
                "odor": "💨", "diplomatic": "🌍", "banana_gc": "🍌",
                "observe": "👁️", "history_rewrite": "📜",
            }.get(ev.kind, "·")
            print(f"  step {ev.step:>4} | {icon} [{ev.frontend}] {ev.detail}")

    print(f"\n  Total events: {len(all_events)}")

# ══════════════════════════════════════════════════════════════
# § 10  Main
# ══════════════════════════════════════════════════════════════

def banner(t): print(f"\n{'━'*64}\n  {t}\n{'━'*64}")
TRUE_VAL  = PoopSucc(PoopZero())

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    banner("DungLang Civilization v2.0  🦍🔥🍌💨🌍📜")
    print("  DungLang = worldview | MysticIR = verification engine | Federation = civilization simulator")

    all_civ_events = []   # ★ collect all civilization events

    # ────────────────────────────────────────────────────────
    # ① OdorIR Optimizer
    # ────────────────────────────────────────────────────────
    banner("① OdorIR Optimizer — 💨+💨+💨+💨 → OdorLevel(4)")

    # Non-optimized: 4 via PoopSucc chain
    prog_unopt = (
        Assign("x", int_to_expr(4)),   # SuccSuccSuccSuccZero
        OdorFlush(Var("x"), source="Mammoth"),
    )
    prog_opt, opt_rep = optimize_program(prog_unopt)

    print(f"\n  Pre-optimization node count: {opt_rep.original_nodes}")
    print(f"  Post-optimization node count: {opt_rep.optimized_nodes}")
    print(f"  Constant-folding reduction: {opt_rep.folded_odor} nodes reduced")
    for s in prog_opt:
        print(f"  Optimized Stmt: {s}")

    # Philosophy version
    prog_phil = (
        Assign("q1", PhilosophyExpr("What is flatulence?")),
        Assign("q2", PhilosophyExpr("What is wind?")),
        Assign("q3", PhilosophyExpr("What is existence?")),
    )
    _, opt_phil = optimize_program(prog_phil)
    print(f"\n  Philosophy calls: {opt_phil.philosophy_calls}")
    print(f"  → Axiom destruction probability: {opt_phil.axiom_break_prob:.1f}%  ⚠️  Danger. UHO!")

    # Execute (with optimization)
    cap, orep = run_capture(prog_unopt, frontend="💩ScatLang", optimize=True)
    if cap.ok():
        for ev in cap.sink.events:
            print(f"  Execution event: {ev.detail}")
            all_civ_events.append(ev)

    # ────────────────────────────────────────────────────────
    # ② Kont Federation — continuation tree identity proof
    # ────────────────────────────────────────────────────────
    banner("② Kont Federation — Continuation tree identity proof")

    common = (
        Assign("x", int_to_expr(3)),
        Assign("y", int_to_expr(2)),
        Flush(OdorAdd(Var("x"), Var("y"))),
    )

    cap_scat, _ = run_capture(common, frontend="💩ScatLang")
    cap_sea,  _ = run_capture(common, frontend="🌊SeaIR")

    # Kont tree snapshot comparison
    print(f"\n  ScatLang Kont tree snapshots ({len(cap_scat.kont_snapshots)}):")
    for snap in cap_scat.kont_snapshots[:3]:
        print(f"    step {snap.step}:")
        print(snap.tree.pretty(3))

    # Identity check
    scat_sigs = [s.signature() for s in cap_scat.kont_snapshots]
    sea_sigs  = [s.signature() for s in cap_sea.kont_snapshots]
    # Compare step and tree only (exclude frontend)
    scat_tree_sigs = [(s, t.signature()) for s, t in
                      [(snap.step, snap.tree) for snap in cap_scat.kont_snapshots]]
    sea_tree_sigs  = [(s, t.signature()) for s, t in
                      [(snap.step, snap.tree) for snap in cap_sea.kont_snapshots]]
    kont_equal = scat_tree_sigs == sea_tree_sigs
    print(f"\n  Kont tree identity: {'✅ Identical! UHO' if kont_equal else '❌ Differences found'}")
    print(f"  (Surface religions may differ, but the shape of continuations is the same. UHO 🪨)")

    # ────────────────────────────────────────────────────────
    # ③ History Federation — history gets rewritten
    # ────────────────────────────────────────────────────────
    banner("③ History Federation — erasing history with bananas UHO 📜🍌")

    sink_hist = CivilizationSink(frontend="🦍DungLang")
    sink_hist.step_count = 17
    sink_hist.observe_odor(7, "Mammoth")
    sink_hist.step_count = 42
    try:
        sink_hist.observe_diplomatic(7, "UhoTribe", "BananaTribe")
    except CrossBorderOdorError:
        pass
    sink_hist.step_count = 88

    print(f"\n  Current history ({len(sink_hist.live_history)} event(s)):")
    for ev in sink_hist.live_history:
        print(f"    step {ev.step}: {ev.detail}")

    print(f"\n  🍌 Inserting 3 bananas...")
    erased = sink_hist.banana_gc(3)
    print(f"  {erased} history event(s) erased")

    print(f"\n  Erased history (HistoryRewriteEvent):")
    for hrev in sink_hist.erased_events:
        print(f"    「{hrev.erased_event}」→ {hrev.rewritten_as}")
        all_civ_events.append(hrev)

    print(f"  Current official history: {len(sink_hist.live_history)} event(s) (blank)")

    # ────────────────────────────────────────────────────────
    # ④ Mammoth Distributed Transaction — Ghost Odor
    # ────────────────────────────────────────────────────────
    banner("④ Mammoth Distributed Transaction — Ghost Odor 👻")

    # CaveA: odor emission success
    cave_a = (OdorFlush(int_to_expr(5), source="Mammoth"),)
    # CaveB: fail with unbound variable (rollback)
    cave_b = (Flush(Var("missing_observer")),)

    ghost = mammoth_distributed_transaction(cave_a, cave_b)
    if ghost:
        all_civ_events.append(ghost)

    # ────────────────────────────────────────────────────────
    # ⑥ Gorilla Incompleteness Theorem
    # ────────────────────────────────────────────────────────
    banner("⑥ Gorilla Incompleteness Theorem — neither can be proved. UHO")

    GorillaTheoremProver.print_theorem()
    print()

    for stmt in ["fart = wind", "fart ≠ wind", "fart ∈ {wind, fart}"]:
        r = GorillaTheoremProver.prove(stmt)
        print(f"  Proving: '{r['statement']}'")
        print(f"    result: {r['result']}")
        print(f"    reason: {r['reason']}")
        print(f"    ({r['theorem']})")
        print()

    # ────────────────────────────────────────────────────────
    # ★ Replay Civilization
    # ────────────────────────────────────────────────────────
    banner("★ Replay Civilization — replaying the full history of civilization UHO 📜")

    # Additional events (from OdorFlush execution)
    for ev in cap.sink.events:
        if ev not in all_civ_events:
            all_civ_events.append(ev)

    replay_civilization(all_civ_events)

    # ────────────────────────────────────────────────────────
    # Summary
    # ────────────────────────────────────────────────────────
    banner("DungLang Civilization v2.0 — Complete Form UHO 🦍🔥🌴💩🌊🍠📜")
    print("""
  ① OdorIR Optimizer      → 💨×4 → OdorLevel(4) constant-folded    ✅
  ② Kont Federation       → Kont tree shape identity proven             ✅
  ③ History Federation    → history revision with bananas / HistoryRewrite ✅
  ④ Ghost Odor            → distributed transaction failure model       ✅
  ⑥ Gorilla Incompleteness→ neither provable                            ✅
  ★ Replay Civilization  → civilization event-sourcing replay           ✅

  Success is the same. Failure is the same.
  Even when history is erased, the event log remains.
  Even when gorilla tries to prove, the theorem collapses.
  This is civilization. UHO. 🪨🔥

  v2.1 Roadmap:
    ⑤ Cave WebSocket (OdorEvent real-time streaming)
    v3.0 pip install dunglang 🍌🔥
""")

    # Save JSON
    out = "/mnt/user-data/outputs/dunglang_civilization_v2_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {"civilization_events": [e.to_dict() for e in all_civ_events]},
            f, ensure_ascii=False, indent=2
        )
    print(f"  Report saved: {out}")

if __name__ == "__main__":
    main()
