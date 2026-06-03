# -*- coding: utf-8 -*-
"""
DungLang Federation 1.0
========================
  DungLang  ──┐
  ScatLang  ──┼──→  OdorIR  ──→  CEK Cave Machine  ──→  OdorSink
  SeaIR     ──┤                                         ↓
  YakiimoIR ──┘                              Error Federation (representative case check)

Presentation prototype. Not a complete compiler or formal proof. UHO.

A connection experiment loading DungLang v0.7 patched odor events into
MysticIR Federation v0.8.5-style trace / observation / error reports.
Verifies federation shape via representative cases. 🪨💨🍌🌊🔥

Notes:
  - DungLang frontend is not a complete DungLang parser;
    it maps v0.7 patched event structures to OdorIR.
  - PhilosophyGorillaError comparison is a minimal comparison running the same IR
    under different frontend names; it is not a federation proof for different syntax parsers.
  - BananaGC is a Sink post-processing event in this demo, not a CEK internal instruction.
  - DiplomaticFlush is a demo design treating diplomatic incidents as both
    observation events and ErrorEvents.
"""
from __future__ import annotations
import json, re, sys, random
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")

# ══════════════════════════════════════════════════════════════
# § 0  Value System (MysticIR inherited + DungLang extended)
# ══════════════════════════════════════════════════════════════

class ScatError(Exception): pass
class ParseError(ScatError): pass
class StepLimitError(ScatError): pass

# ── DungLang Federation new exceptions ──
class PhilosophyGorillaError(ScatError):
    """The moment an observer smells something, a question arises. UHO"""
class AxiomDestructionError(ScatError):
    """When PhilosophyGorilla philosophizes its own flatulence, the universe contradicts. UHO"""
class BananaShortageError(ScatError):
    """Not enough bananas for cognitive GC. UHO"""
class CrossBorderOdorError(ScatError):
    """Diplomatic incident when inter-tribe treaty value is exceeded. UHO"""

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

# ── DungLang extended values ──
@dataclass(frozen=True)
class OdorValue(Value):
    """Extended value holding odor level as a Peano number. UHO"""
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

TRUE  = PoopSucc(PoopZero())
FALSE = PoopZero()

# ══════════════════════════════════════════════════════════════
# § 1  OdorIR — Common Intermediate Representation
#       All frontends are converted to this
# ══════════════════════════════════════════════════════════════

class Expr: pass

@dataclass(frozen=True)
class OdorZeroExpr(Expr): pass          # OdorZero (odorless)

@dataclass(frozen=True)
class OdorSuccExpr(Expr):               # OdorLevel +1
    expr: Expr

@dataclass(frozen=True)
class PoopZeroExpr(Expr): pass          # MysticIR compatible

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

# ── DungLang-specific IR expressions ──
@dataclass(frozen=True)
class PhilosophyExpr(Expr):
    """IR expression representing PhilosophyGorilla's question. Evaluating it raises PhilosophyGorillaError. UHO"""
    question: str

@dataclass(frozen=True)
class BananaExpr(Expr):
    """IR expression representing n bananas. Triggers cognitive GC. UHO"""
    count: Expr

class Stmt: pass

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
    """Odor-observation-only flush. Flows into OdorSink. UHO"""
    expr: Expr
    source: str = "unknown"

@dataclass(frozen=True)
class DiplomaticFlush(Stmt):
    """Flushes cross-border odor into the diplomatic sink. UHO"""
    expr: Expr
    from_tribe: str
    to_tribe:   str

# ══════════════════════════════════════════════════════════════
# § 2  OdorSink — ObservationSink extension
#       💨→diplomatic incident→reparation→forgetting  all recorded in Trace. UHO
# ══════════════════════════════════════════════════════════════

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

# Inter-tribe treaty values
TREATY = {
    ("UhoTribe",    "BananaTribe"):    3,
    ("UhoTribe",    "MammothTribe"):   5,
    ("BananaTribe", "MammothTribe"):   4,
}

@dataclass
class OdorSink:
    """
    ObservationSink
         ↓
       OdorSink
         ↓
    DiplomaticSink
         ↓
    BananaGCSink
    """
    _observations: list = field(default_factory=list)
    _odor_events:  list = field(default_factory=list)
    _diplo_events: list = field(default_factory=list)
    _gc_events:    list = field(default_factory=list)
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
            verdict       = "DiplomaticIncident"
            banana_penalty = level * 2
        else:
            verdict       = "WeatherGorillaFault"
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
    def observations(self): return tuple(self._observations)
    @property
    def odor_events(self):  return tuple(self._odor_events)
    @property
    def diplo_events(self): return tuple(self._diplo_events)
    @property
    def gc_events(self):    return tuple(self._gc_events)
    @property
    def memory_buffer(self): return list(self._memory_buffer)

# ══════════════════════════════════════════════════════════════
# § 3  CEK Cave Machine — MysticIR inherited + OdorIR support
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
    """Continuation for odor observation. UHO"""
    rest: tuple; env: Any; kont: Kont; source: str

@dataclass(frozen=True)
class DiplomaticFlushK(Kont):
    """Diplomatic continuation. UHO"""
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
    if b.to_int() == 0: raise ScatError("mod by zero")
    return int_to_poop(a.to_int() % b.to_int())
def poop_eq(a, b):  return TRUE if a.to_int() == b.to_int() else FALSE
def poop_neq(a, b): return TRUE if a.to_int() != b.to_int() else FALSE

def step(state: State) -> State:
    state.sink.tick()
    ctrl = state.control

    # ── StmtSeq ──
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

    # ── EvalExpr ──
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
            # PhilosophyGorilla's question drifts the moment it is evaluated. UHO
            raise PhilosophyGorillaError(e.question)
        if isinstance(e, BananaExpr):
            return State(EvalExpr(e.count), state.env, state.kont, state.sink)
        raise ScatError(f"unknown expr: {e!r}")

    # ── ReturnValue ──
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
# § 4  TraceEvent — MysticIR compatible + OdorSink extended
# ══════════════════════════════════════════════════════════════

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
    final_state: object; trace: TraceCollector; error: object
    def ok(self): return self.error is None

def kont_depth_fn(k):
    d = 0
    while not isinstance(k, Halt):
        d += 1; k = getattr(k, 'kont', None)
        if k is None: break
    return d

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

def run_capture(prog, env=None, *, frontend, max_steps=200_000):
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
# § 5  Frontends × 3 + DungLang
#       All converted to OdorIR and run on CEK Cave Machine. UHO
# ══════════════════════════════════════════════════════════════

# ── 5a. ScatLang Frontend (💩 notation) ──
# Written directly as IR tuples (parser omitted — essence only). UHO

def scatlang_mod_by_zero():
    return (
        Assign("x", OdorMod(int_to_value_expr(3), int_to_value_expr(0))),
    )

def int_to_value_expr(n):
    e = PoopZeroExpr()
    for _ in range(n): e = PoopSuccExpr(e)
    return e

def scatlang_unbound():
    return (Flush(Var("missing")),)

def scatlang_infinite():
    return (While(int_to_value_expr(0), PoopSuccExpr(PoopZeroExpr()), (
        Assign("x", PoopZeroExpr()),
    )),)

# ── 5b. SeaIR Frontend (🌊 notation) ──  runs same IR under different frontend name

def seair_mod_by_zero():    return scatlang_mod_by_zero()
def seair_unbound():        return scatlang_unbound()
def seair_infinite():       return scatlang_infinite()

# ── 5c. YakiimoIR Frontend (🍠 roasted-yam notation) ──  DungLang concepts expressed directly in IR

def yakiimo_philosophy():
    """PhilosophyGorilla philosophizes flatulence — axiom destruction. UHO"""
    return (
        Assign("question", PhilosophyExpr("To whom does the flatulence belong? UHO")),
        Flush(Var("question")),
    )

def yakiimo_diplomatic():
    """Cross-border odor (concentration 7) — diplomatic incident. UHO"""
    return (
        DiplomaticFlush(int_to_value_expr(7), "UhoTribe", "BananaTribe"),
    )

def yakiimo_banana_gc():
    """3 bananas → GC — memory forgotten. UHO"""
    # Dummy Flush: after BananaExpr evaluation, call GC directly on Sink
    return (
        Assign("banana", BananaExpr(int_to_value_expr(3))),
        Flush(Var("banana")),
    )

# ── 5d. DungLang Frontend (🦍 cave notation) ──
#     Manually "compile" DungLang v0.7 source to OdorIR

def dunglang_compile(phenomenon: dict):
    """
    Maps a DungLang v0.7 patched event structure (dict) to OdorIR Stmt tuples.
    Not a full DungLang parser — a demo mapping v0.7 "smell/suspect/side_effect_level"
    onto OdorIR Stmts.

    Example input:
      {"smell": "omnidirectional", "suspect": "Mammoth", "side_effect_level": 3}
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
    # Cross-border check (if omnidirectional, activate diplomatic module)
    if phenomenon.get("smell") == "omnidirectional":
        stmts.append(DiplomaticFlush(int_to_value_expr(total_level), "UhoTribe", "BananaTribe"))
    return tuple(stmts)

# ══════════════════════════════════════════════════════════════
# § 6  Error Federation Representative Case Check
#       Verifies via representative cases whether PhilosophyGorillaError stalls at the same Kont and step. UHO
#       NOTE: This is a connection experiment, not a federation proof for different syntax parsers
# ══════════════════════════════════════════════════════════════

def paired_error_report(name, prog_a, frontend_a, prog_b, frontend_b, max_steps=200_000):
    cap_a = run_capture(prog_a, frontend=frontend_a, max_steps=max_steps)
    cap_b = run_capture(prog_b, frontend=frontend_b, max_steps=max_steps)
    assert cap_a.error and cap_b.error, f"{name}: both must fail"
    return {
        "case":             name,
        "trace_equal":      cap_a.trace.signature() == cap_b.trace.signature(),
        "error_equal":      cap_a.error.signature() == cap_b.error.signature(),
        "surface_diff":     (cap_a.error.signature(include_frontend=True)
                             != cap_b.error.signature(include_frontend=True)),
        "step_left":        len(cap_a.trace.events),
        "step_right":       len(cap_b.trace.events),
        "left_error":       cap_a.error.to_dict(),
        "right_error":      cap_b.error.to_dict(),
    }

# ══════════════════════════════════════════════════════════════
# § 7  Main Execution
# ══════════════════════════════════════════════════════════════

def banner(t): print(f"\n{'━'*62}\n  {t}\n{'━'*62}")

def run_demo(name, prog, frontend, max_steps=200_000, show_odor=True):
    cap = run_capture(prog, frontend=frontend, max_steps=max_steps)
    mark = "✅" if cap.ok() else "❌"
    print(f"\n  {mark} [{frontend}] {name}")
    if cap.ok() and cap.final_state:
        obs = cap.final_state.sink.observations
        for o in obs:
            print(f"     observed: {o.artifact.value.pretty()} @ step {o.artifact.born_at_step}")
        if show_odor:
            for ev in cap.final_state.sink.odor_events:
                print(f"     💨 OdorLv{ev.level}({ev.source}) @ step {ev.step}")
            for ev in cap.final_state.sink.diplo_events:
                print(f"     🌍 Diplomacy:{ev.verdict} {ev.from_tribe}→{ev.to_tribe} "
                      f"concentration={ev.level} banana={ev.banana_penalty} @ step {ev.step}")
            for ev in cap.final_state.sink.gc_events:
                print(f"     🍌 GC: banana×{ev.banana_count} → {ev.erased_count} event(s) forgotten @ step {ev.step}")
        if not obs and not cap.final_state.sink.odor_events:
            print(f"     (no observations)")
    if not cap.ok():
        e = cap.error
        print(f"     {e.error_type}({e.error_message}) @ step {e.step} "
              f"kont={e.kont_kind} depth={e.kont_depth}")

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    banner("DungLang Federation 1.0 🦍🔥🪨")
    print("""
  DungLang  ──┐
  ScatLang  ──┼──→  OdorIR  ──→  CEK Cave Machine  ──→  OdorSink
  SeaIR     ──┤                                           ↓
  YakiimoIR ──┘                              Error Federation (representative case check)

  Presentation prototype. Not a complete compiler or formal proof. UHO.
  Connecting DungLang v0.7 patched odor events to
  MysticIR v0.8.5-style trace / error reports. 🪨💨🍌🌊🔥
""")

    # ── Part 1: DungLang Frontend Demo ──
    banner("Part 1 — DungLang Frontend (v0.7 event structure → OdorIR mapping → CEK)")

    phenomenon = {"smell": "omnidirectional", "suspect": "Mammoth", "side_effect_level": 3}
    prog_dung = dunglang_compile(phenomenon)
    print(f"\n  DungLang v0.7 event structure: {phenomenon}")
    print(f"  OdorIR mapping result → ({len(prog_dung)} stmt):")
    for i, s in enumerate(prog_dung):
        print(f"    [{i}] {s}")

    # Diplomatic incident → CrossBorderOdorError drifts (recorded as error). UHO
    cap = run_capture(prog_dung, frontend="🦍DungLang", max_steps=200_000)
    if not cap.ok():
        e = cap.error
        print(f"\n  🌍 Diplomatic handling: {e.error_type}")
        print(f"     {e.error_message}")
        # Retrieve OdorSink records manually (final_state is None on error)
        print(f"     → Blame engine: WeatherGorillaFault (convention)")
    
    # Harmless version (no cross-border)
    phenom2 = {"smell": "faint", "suspect": "roasted-yam", "side_effect_level": 1}
    prog2   = dunglang_compile(phenom2)
    run_demo("DungLang Demo (faint odor, harmless)", prog2, "🦍DungLang")

    # ── Part 2: 3 Frontend Success Demo ──
    banner("Part 2 — 3 Frontend Success Demo (identical CEK transitions)")

    # Common program: x ← 5, flush x
    common_prog = (
        Assign("x", int_to_value_expr(5)),
        Flush(Var("x")),
    )
    for fe in ["💩ScatLang", "🌊SeaIR", "🍠YakiimoIR"]:
        run_demo("x=5, flush x", common_prog, fe, show_odor=False)

    # ── Part 3: YakiimoIR New Feature Demo ──
    banner("Part 3 — YakiimoIR New Features (Philosophy / Diplomacy / Banana GC)")

    run_demo("PhilosophyGorilla's flatulence (axiom destruction)",
             yakiimo_philosophy(), "🍠YakiimoIR")
    run_demo("Cross-border odor (diplomatic incident, concentration 7)",
             yakiimo_diplomatic(), "🍠YakiimoIR")

    # Banana GC succeeds. UHO
    # NOTE: not a CEK internal instruction; treated as Sink post-processing event in this demo
    cap_gc = run_capture(yakiimo_banana_gc(), frontend="🍠YakiimoIR")
    gc_result = cap_gc.final_state.sink.banana_gc(3) if cap_gc.ok() else None
    print(f"\n  ✅ [🍠YakiimoIR] Banana GC Demo")
    if gc_result:
        print(f"     🍌 banana×{gc_result.banana_count} → {gc_result.erased_count} event(s) forgotten")
        print(f"     \"Was there something? Eh, whatever. UHO 🍌\"")

    # ── Part 4: Error Federation Check ──
    banner("Part 4 — Error Federation Representative Case Check (does PhilosophyGorilla also stall at same Kont?)")

    ERROR_CASES = [
        ("mod by zero",
         scatlang_mod_by_zero(), "💩ScatLang",
         seair_mod_by_zero(),    "🌊SeaIR",
         200_000),
        ("unbound variable",
         scatlang_unbound(),     "💩ScatLang",
         seair_unbound(),        "🌊SeaIR",
         200_000),
        ("step limit / constipation",
         scatlang_infinite(),    "💩ScatLang",
         seair_infinite(),       "🌊SeaIR",
         40),
        ("PhilosophyGorillaError (DungLang vs YakiimoIR)",
         # NOTE: Minimal comparison running same IR under different frontend names. Not proof of different syntax parsers.
         yakiimo_philosophy(),   "🦍DungLang",
         yakiimo_philosophy(),   "🍠YakiimoIR",
         200_000),
    ]

    reports = []
    all_ok  = True
    print()
    for case_args in ERROR_CASES:
        name, pa, fa, pb, fb, ms = case_args
        r  = paired_error_report(name, pa, fa, pb, fb, max_steps=ms)
        ok = r["trace_equal"] and r["error_equal"] and r["surface_diff"]
        all_ok = all_ok and ok
        mark = "✅" if ok else "❌"
        le   = r["left_error"]
        print(f"  {mark} {r['case']}")
        print(f"     steps:        {r['step_left']} == {r['step_right']}")
        print(f"     trace sig:    {r['trace_equal']}")
        print(f"     error sig:    {r['error_equal']}")
        print(f"     surface diff: {r['surface_diff']}")
        print(f"     error:        {le['error_type']}({le['error_message']}) "
              f"@ step {le['step']} kont={le['kont_kind']}")
        print()
        reports.append(r)

    # Save JSON
    out = "/mnt/user-data/outputs/dunglang_federation_1_0_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"cases": reports}, f, ensure_ascii=False, indent=2)

    # ── Summary ──
    banner("Federation Representative Case Check Complete 🦍🔥🌴💩🌊🍠")
    print("""
  DungLang v0.7  (OdorMonad / Diplomacy / GC)        : source event structure   ✅
  MysticIR v0.8.5 (CEK / Error Federation)            : execution engine         ✅
  DungLang Federation 1.0 (OdorIR / OdorSink)         : connection demo complete ✅

  Representative case scope:
    mod by zero         → same step, same Kont, same error confirmed    ✅
    unbound variable    → same step, same Kont, same error confirmed    ✅
    constipation (∞ loop) → same step, same Kont, same stall confirmed  ✅
    PhilosophyGorillaError → minimal comparison with same IR (confirmed) ✅

  Notes:
    - Not a complete compiler or exhaustive proof.
    - DungLang frontend is a demo mapping v0.7 event structures to OdorIR.
    - Surface syntax may differ, but underground plumbing confirmed via representative cases. UHO 🪨
""")
    if all_ok:
        print("  DungLang Federation 1.0 representative case check complete. UHO 🦍🔥🪨")
    else:
        print("  ❌ Some mismatch — PhilosophyGorilla may be involved. UHO")

if __name__ == "__main__":
    main()
