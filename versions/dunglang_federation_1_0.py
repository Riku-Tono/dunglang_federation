# -*- coding: utf-8 -*-
"""
DungLang Federation 1.0
========================
  DungLang  ──┐
  ScatLang  ──┼──→  臭気IR  ──→  CEK洞窟マシン  ──→  OdorSink
  SeaIR     ──┤                                         ↓
  YakiimoIR ──┘                              Error Federation（代表ケース確認）

発表用プロトタイプ。完全なコンパイラや完全証明ではないウホ。

DungLang v0.7 patched の臭気イベントを、
MysticIR Federation v0.8.5 型の trace / observation / error report に
載せる接続実験です。代表ケースで federation 形状を確認するものです。🪨💨🍌🌊🔥

注記:
  - DungLang frontend は完全な DungLang パーサーではなく、
    v0.7 patched のイベント構造を臭気IRへ写像するものです。
  - 哲学ゴリラ例外の比較は、同一IRを別frontend名で実行する最小比較であり、
    異なる構文パーサーの federation 証明ではありません。
  - BananaGC は今回のデモでは CEK内部命令ではなく Sink 後処理イベントです。
  - DiplomaticFlush は外交問題を観測イベントかつ ErrorEvent として
    扱うデモ設計です。
"""
from __future__ import annotations
import json, re, sys, random
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")

# ══════════════════════════════════════════════════════════════
# § 0  値システム（MysticIR継承 + DungLang拡張）
# ══════════════════════════════════════════════════════════════

class ScatError(Exception): pass
class ParseError(ScatError): pass
class StepLimitError(ScatError): pass

# ── DungLang Federation 新規例外 ──
class 哲学ゴリラ例外(ScatError):
    """観測者が臭いを感じた瞬間、問いが発生するウホ"""
class 公理破壊例外(ScatError):
    """哲学ゴリラが自分のおならに哲学した場合、宇宙の矛盾ウホ"""
class バナナ不足例外(ScatError):
    """認知GCに必要なバナナが足りないウホ"""
class 越境臭気例外(ScatError):
    """部族間条約値を超えた場合の外交問題ウホ"""

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

# ── DungLang拡張値 ──
@dataclass(frozen=True)
class OdorValue(Value):
    """臭気レベルをペアノ数で持つ拡張値ウホ"""
    level: Value
    source: str = "不明"
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
# § 1  臭気IR — 共通中間表現
#       全フロントエンドはここへ変換する
# ══════════════════════════════════════════════════════════════

class Expr: pass

@dataclass(frozen=True)
class OdorZeroExpr(Expr): pass          # 臭気ゼロ（無臭）

@dataclass(frozen=True)
class OdorSuccExpr(Expr):               # 臭気レベル+1
    expr: Expr

@dataclass(frozen=True)
class PoopZeroExpr(Expr): pass          # MysticIR互換

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

# ── DungLang専用IR式 ──
@dataclass(frozen=True)
class PhilosophyExpr(Expr):
    """哲学ゴリラの問いを表すIR式。評価すると哲学ゴリラ例外が漂うウホ"""
    question: str

@dataclass(frozen=True)
class BananaExpr(Expr):
    """バナナn本を表すIR式。認知GCのトリガーウホ"""
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
    """臭気観測専用flush。OdorSinkへ流れるウホ"""
    expr: Expr
    source: str = "不明"

@dataclass(frozen=True)
class DiplomaticFlush(Stmt):
    """越境臭気を外交Sinkへ流すウホ"""
    expr: Expr
    from_tribe: str
    to_tribe:   str

# ══════════════════════════════════════════════════════════════
# § 2  OdorSink — ObservationSinkの拡張
#       💨→外交問題→賠償→忘却  全部Traceに残るウホ
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

# 部族間条約値
TREATY = {
    ("ウホ族",   "バナナ族"): 3,
    ("ウホ族",   "マンモス部族"): 5,
    ("バナナ族", "マンモス部族"): 4,
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
        self._memory_buffer.append(f"臭気Lv{level}({source})")

    def observe_diplomatic(self, level: int, from_t: str, to_t: str) -> DiplomaticEvent:
        treaty_val = TREATY.get((from_t, to_t), 4)
        if level > treaty_val:
            verdict       = "外交問題"
            banana_penalty = level * 2
        else:
            verdict       = "気象ゴリラのせい"
            banana_penalty = 0
        ev = DiplomaticEvent(self.step_count, level, from_t, to_t, verdict, banana_penalty)
        self._diplo_events.append(ev)
        self._memory_buffer.append(f"外交:{verdict}({from_t}→{to_t})")
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
# § 3  CEK洞窟マシン — MysticIR継承 + 臭気IR対応
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
    """臭気観測用継続ウホ"""
    rest: tuple; env: Any; kont: Kont; source: str

@dataclass(frozen=True)
class DiplomaticFlushK(Kont):
    """外交継続ウホ"""
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
            # 哲学ゴリラの問いは評価した瞬間に漂うウホ
            raise 哲学ゴリラ例外(e.question)
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
            if ev.verdict == "外交問題":
                raise 越境臭気例外(
                    f"{k.from_tribe}→{k.to_tribe} 濃度{v.to_int()} "
                    f"バナナ{ev.banana_penalty}本賠償"
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
# § 4  TraceEvent — MysticIR互換 + OdorSink拡張
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
# § 5  フロントエンド × 3 + DungLang
#       全部が臭気IRへ変換されCEK洞窟マシンで動くウホ
# ══════════════════════════════════════════════════════════════

# ── 5a. ScatLang Frontend（💩 記法） ──
# 直接IRタプルで書くウホ（パーサー省略・本質だけ）

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

# ── 5b. SeaIR Frontend（🌊 記法）──  同じIRを別フロントエンド名で実行

def seair_mod_by_zero():    return scatlang_mod_by_zero()
def seair_unbound():        return scatlang_unbound()
def seair_infinite():       return scatlang_infinite()

# ── 5c. YakiimoIR Frontend（🍠 焼き芋記法）──  DungLang概念をIRで直表現

def yakiimo_philosophy():
    """哲学ゴリラがおならを哲学する——公理破壊ウホ"""
    return (
        Assign("question", PhilosophyExpr("おならとは誰のものかウホ")),
        Flush(Var("question")),
    )

def yakiimo_diplomatic():
    """越境臭気（濃度7）——外交問題ウホ"""
    return (
        DiplomaticFlush(int_to_value_expr(7), "ウホ族", "バナナ族"),
    )

def yakiimo_banana_gc():
    """バナナ3本でGC——記憶忘却ウホ"""
    # BananaExpr評価後、GCをSinkに直接呼ぶダミーFlush
    return (
        Assign("banana", BananaExpr(int_to_value_expr(3))),
        Flush(Var("banana")),
    )

# ── 5d. DungLang Frontend（🦍 洞窟記法）──
#     DungLang v0.7ソースを臭気IRへ手動「コンパイル」

def dunglang_compile(phenomenon: dict):
    """
    DungLang v0.7 patched のイベント構造（dict）を臭気IR Stmt tuple へ写像する。
    完全な DungLang パーサーではなく、v0.7 の「臭い/容疑者/副作用レベル」を
    臭気IRの Stmt に対応付ける写像デモです。

    入力例:
      {"臭い": "全方位", "容疑者": "マンモス", "副作用レベル": 3}
    """
    odor_level  = {"無臭": 0, "微臭": 1, "強臭": 3, "全方位": 7}.get(
                    phenomenon.get("臭い", "微臭"), 2)
    fart_count  = phenomenon.get("副作用レベル", 0)
    suspect     = phenomenon.get("容疑者", "不明")
    total_level = odor_level + fart_count

    stmts = [
        Assign("odor_level", int_to_value_expr(total_level)),
        OdorFlush(int_to_value_expr(total_level), source=suspect),
    ]
    # 越境判定（全方位なら外交モジュール起動）
    if phenomenon.get("臭い") == "全方位":
        stmts.append(DiplomaticFlush(int_to_value_expr(total_level), "ウホ族", "バナナ族"))
    return tuple(stmts)

# ══════════════════════════════════════════════════════════════
# § 6  Error Federation 代表ケース確認
#       哲学ゴリラ例外も「同じKontで同じstepで詰まるか」を代表ケースで確認するウホ
#       ※ 異なる構文パーサーの federation 証明ではなく、接続実験です
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
# § 7  メイン実行
# ══════════════════════════════════════════════════════════════

def banner(t): print(f"\n{'━'*62}\n  {t}\n{'━'*62}")

def run_demo(name, prog, frontend, max_steps=200_000, show_odor=True):
    cap = run_capture(prog, frontend=frontend, max_steps=max_steps)
    mark = "✅" if cap.ok() else "❌"
    print(f"\n  {mark} [{frontend}] {name}")
    if cap.ok() and cap.final_state:
        obs = cap.final_state.sink.observations
        for o in obs:
            print(f"     観測値: {o.artifact.value.pretty()} @ step {o.artifact.born_at_step}")
        if show_odor:
            for ev in cap.final_state.sink.odor_events:
                print(f"     💨 臭気Lv{ev.level}({ev.source}) @ step {ev.step}")
            for ev in cap.final_state.sink.diplo_events:
                print(f"     🌍 外交:{ev.verdict} {ev.from_tribe}→{ev.to_tribe} "
                      f"濃度{ev.level} バナナ{ev.banana_penalty}本 @ step {ev.step}")
            for ev in cap.final_state.sink.gc_events:
                print(f"     🍌 GC: バナナ{ev.banana_count}本で{ev.erased_count}件忘却 @ step {ev.step}")
        if not obs and not cap.final_state.sink.odor_events:
            print(f"     （観測なし）")
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
  ScatLang  ──┼──→  臭気IR  ──→  CEK洞窟マシン  ──→  OdorSink
  SeaIR     ──┤                                         ↓
  YakiimoIR ──┘                              Error Federation（代表ケース確認）

  発表用プロトタイプ。完全なコンパイラや完全証明ではないウホ。
  DungLang v0.7 patched の臭気イベントを
  MysticIR v0.8.5 型の trace / error report へ写像する接続実験です。🪨💨🍌🌊🔥
""")

    # ── Part 1: DungLang Frontend デモ ──
    banner("Part 1 — DungLang Frontend（v0.7イベント構造 → 臭気IR写像 → CEK）")

    phenomenon = {"臭い": "全方位", "容疑者": "マンモス", "副作用レベル": 3}
    prog_dung = dunglang_compile(phenomenon)
    print(f"\n  DungLang v0.7 イベント構造: {phenomenon}")
    print(f"  臭気IRへの写像結果 → ({len(prog_dung)} stmt):")
    for i, s in enumerate(prog_dung):
        print(f"    [{i}] {s}")

    # 外交問題なので越境臭気例外が漂うウホ（エラーとして記録）
    cap = run_capture(prog_dung, frontend="🦍DungLang", max_steps=200_000)
    if not cap.ok():
        e = cap.error
        print(f"\n  🌍 外交処理: {e.error_type}")
        print(f"     {e.error_message}")
        # OdorSinkの記録を手動取得（エラー時はfinal_stateがNone）
        print(f"     → 責任転嫁エンジン: 気象ゴリラのせい（慣例）")
    
    # 無害バージョン（越境しない）
    phenom2 = {"臭い": "微臭", "容疑者": "焼き芋", "副作用レベル": 1}
    prog2   = dunglang_compile(phenom2)
    run_demo("DungLangデモ（微臭・無害）", prog2, "🦍DungLang")

    # ── Part 2: 3フロントエンド成功デモ ──
    banner("Part 2 — 3フロントエンド成功デモ（同一CEK遷移）")

    # 共通プログラム: x ← 5, flush x
    common_prog = (
        Assign("x", int_to_value_expr(5)),
        Flush(Var("x")),
    )
    for fe in ["💩ScatLang", "🌊SeaIR", "🍠YakiimoIR"]:
        run_demo("x=5, flush x", common_prog, fe, show_odor=False)

    # ── Part 3: YakiimoIR 新機能デモ ──
    banner("Part 3 — YakiimoIR 新機能（哲学・外交・バナナGC）")

    run_demo("哲学ゴリラのおなら（公理破壊）",
             yakiimo_philosophy(), "🍠YakiimoIR")
    run_demo("越境臭気（外交問題・濃度7）",
             yakiimo_diplomatic(), "🍠YakiimoIR")

    # バナナGCは成功するウホ
    # ※ CEK内部命令ではなく、今回のデモでは Sink 後処理イベントとして扱う
    cap_gc = run_capture(yakiimo_banana_gc(), frontend="🍠YakiimoIR")
    gc_result = cap_gc.final_state.sink.banana_gc(3) if cap_gc.ok() else None
    print(f"\n  ✅ [🍠YakiimoIR] バナナGCデモ")
    if gc_result:
        print(f"     🍌 バナナ{gc_result.banana_count}本投入 → {gc_result.erased_count}件忘却")
        print(f"     「何かあったっけ？まあいいウホ🍌」")

    # ── Part 4: Error Federation 証明 ──
    banner("Part 4 — Error Federation 代表ケース確認（哲学ゴリラも同じKontで詰まるか）")

    ERROR_CASES = [
        ("mod by zero",
         scatlang_mod_by_zero(), "💩ScatLang",
         seair_mod_by_zero(),    "🌊SeaIR",
         200_000),
        ("unbound variable",
         scatlang_unbound(),     "💩ScatLang",
         seair_unbound(),        "🌊SeaIR",
         200_000),
        ("step limit / 便秘",
         scatlang_infinite(),    "💩ScatLang",
         seair_infinite(),       "🌊SeaIR",
         40),
        ("哲学ゴリラ例外（DungLang vs YakiimoIR）",
         # ※ 同一IRを別frontend名で実行する最小比較。異なる構文パーサーの証明ではない。
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

    # JSON保存
    out = "/mnt/user-data/outputs/dunglang_federation_1_0_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"cases": reports}, f, ensure_ascii=False, indent=2)

    # ── 総括 ──
    banner("Federation 代表ケース確認 完了 🦍🔥🌴💩🌊🍠")
    print("""
  DungLang v0.7  (臭気モナド・外交・GC)              : 写像元イベント構造  ✅
  MysticIR v0.8.5 (CEK・Error Federation)            : 実行エンジン        ✅
  DungLang Federation 1.0 (臭気IR・OdorSink)         : 接続実験完了        ✅

  代表ケース確認スコープ:
    mod by zero         → 同じstepで同じKontで同じエラーを確認    ✅
    unbound variable    → 同じstepで同じKontで同じエラーを確認    ✅
    便秘(無限ループ)    → 同じstepで同じKontで同じ詰まりを確認    ✅
    哲学ゴリラ例外      → 同一IRを別frontend名で最小比較（確認）  ✅

  注記:
    - 完全なコンパイラや全ケース網羅の証明ではありません。
    - DungLang frontend は v0.7 イベント構造を臭気IRへ写像するデモです。
    - 地上の記法が違っても、地下の配管形状を代表ケースで確認しましたウホ🪨
""")
    if all_ok:
        print("  DungLang Federation 1.0 代表ケース確認 完了 ウホ🦍🔥🪨")
    else:
        print("  ❌ 一部不一致 — 哲学ゴリラの仕業か要確認ウホ")

if __name__ == "__main__":
    main()
