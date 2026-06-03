# -*- coding: utf-8 -*-
"""
DungLang Civilization v2.0
===========================
  ① 臭気IR最適化器        (OdorOptimizer)
  ② Kont Federation        (継続木の同一性証明)
  ③ History Federation     (HistoryRewriteEvent — 歴史が書き換わる)
  ④ マンモス分散トランザクション (Ghost Odor)
  ⑥ ゴリラ不完全性定理     (どっちも証明できない)
  ★ Replay Civilization    (文明イベントソーシング再生)

  DungLang = 世界観
  MysticIR = 検証エンジン
  Federation = 文明シミュレータ   🦍🔥🍌💨🌍📜
"""
from __future__ import annotations
import json, re, sys, random, copy
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# ══════════════════════════════════════════════════════════════
# § 0  基盤（Federation 1.0 から継承・最小版）
# ══════════════════════════════════════════════════════════════

class ScatError(Exception): pass
class StepLimitError(ScatError): pass
class 哲学ゴリラ例外(ScatError): pass
class 公理破壊例外(ScatError): pass
class 越境臭気例外(ScatError): pass
class GhostOdorError(ScatError): pass   # ④ 新規

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

# 臭気IR 式・文
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
    """① 最適化後の畳み込み済み臭気レベル"""
    level: int

@dataclass(frozen=True)
class Assign(Stmt): name: str; expr: Expr
@dataclass(frozen=True)
class Flush(Stmt):  expr: Expr
@dataclass(frozen=True)
class OdorFlush(Stmt): expr: Expr; source: str = "不明"
@dataclass(frozen=True)
class DiplomaticFlush(Stmt): expr: Expr; from_tribe: str; to_tribe: str
@dataclass(frozen=True)
class While(Stmt): left: Expr; right: Expr; body: tuple

def int_to_expr(n):
    e = PoopZeroExpr()
    for _ in range(n): e = PoopSuccExpr(e)
    return e

def expr_to_int(e) -> Optional[int]:
    """定数畳み込み用ウホ"""
    if isinstance(e, PoopZeroExpr): return 0
    if isinstance(e, PoopSuccExpr):
        inner = expr_to_int(e.expr)
        return None if inner is None else inner + 1
    if isinstance(e, OdorLevelExpr): return e.level
    return None

# Kontとステート（省略なし）
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
# § 1  臭気IR最適化器 ウホ🔥
#       OdorAdd/PoopSucc 連打 → OdorLevelExpr(n) に畳み込む
#       哲学連打 → 公理破壊確率を事前計算
# ══════════════════════════════════════════════════════════════

@dataclass
class OptimizeReport:
    original_nodes: int
    optimized_nodes: int
    folded_odor: int          # 畳み込んだ臭気ノード数
    philosophy_calls: int     # 哲学呼び出し回数
    axiom_break_prob: float   # 公理破壊確率(%)

def count_nodes(e) -> int:
    if isinstance(e, (PoopZeroExpr, OdorLevelExpr, Var, PhilosophyExpr)): return 1
    if isinstance(e, PoopSuccExpr): return 1 + count_nodes(e.expr)
    if isinstance(e, (OdorAdd, OdorNeq, OdorMod, OdorEq, OdorSub)):
        return 1 + count_nodes(e.left) + count_nodes(e.right)
    if isinstance(e, OdorPred): return 1 + count_nodes(e.expr)
    return 1

def optimize_expr(e: Expr) -> Expr:
    """定数畳み込み + 恒等変換除去ウホ"""
    # PoopSucc連打 → OdorLevelExpr
    v = expr_to_int(e)
    if v is not None:
        return OdorLevelExpr(v)
    # OdorAdd で両辺が定数
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
    # 哲学ゴリラ公理破壊確率: 1回なら低い、3回以上で急増
    prob = min(97.0, phil_calls * 32.3)
    report = OptimizeReport(
        original_nodes=orig_nodes, optimized_nodes=opt_nodes,
        folded_odor=orig_nodes - opt_nodes,
        philosophy_calls=phil_calls, axiom_break_prob=prob,
    )
    return tuple(optimized), report

# ══════════════════════════════════════════════════════════════
# § 2  Kont木 — ② Kont Federation
#       継続スタックを木として記録・比較するウホ
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
# § 3  文明イベント群 — ③ History Federation + ★ Replay
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CivEvent:
    step: int; kind: str; detail: str; frontend: str

    def to_dict(self):
        return dict(step=self.step, kind=self.kind,
                    detail=self.detail, frontend=self.frontend)

@dataclass(frozen=True)
class HistoryRewriteEvent(CivEvent):
    """③ 歴史が書き換わったウホ"""
    erased_event: str = ""
    rewritten_as: str = "最初から存在しなかったことになった"

    def to_dict(self):
        d = super().to_dict()
        d.update(erased_event=self.erased_event,
                 rewritten_as=self.rewritten_as)
        return d

@dataclass(frozen=True)
class GhostOdorEvent(CivEvent):
    """④ Ghost Odor — 臭いだけ存在・犯人不在"""
    cave_a: str = ""; cave_b: str = ""
    odor_level: int = 0

    def to_dict(self):
        d = super().to_dict()
        d.update(cave_a=self.cave_a, cave_b=self.cave_b,
                 odor_level=self.odor_level)
        return d

# ══════════════════════════════════════════════════════════════
# § 4  CivilizationSink — OdorSink の完全体
#       全イベントをイベントソーシングで保存するウホ
# ══════════════════════════════════════════════════════════════

TREATY = {
    ("ウホ族","バナナ族"): 3,
    ("ウホ族","マンモス部族"): 5,
    ("バナナ族","マンモス部族"): 4,
}

@dataclass
class CivilizationSink:
    frontend: str = "unknown"
    step_count: int = 0
    _events: list = field(default_factory=list)           # 全イベント時系列
    _observations: list = field(default_factory=list)
    _kont_snapshots: list = field(default_factory=list)   # ② Kont木スナップショット
    _erased_events: list = field(default_factory=list)    # ③ 消された事件
    _history: list = field(default_factory=list)          # 公式歴史（書き換え後）

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
            verdict, banana = "外交問題", level * 2
            ev = CivEvent(self.step_count, "diplomatic",
                          f"🌍 {ft}→{tt} 濃度{level} バナナ{banana}本", self.frontend)
            self._emit(ev)
            raise 越境臭気例外(f"{ft}→{tt} 濃度{level} バナナ{banana}本賠償")
        else:
            ev = CivEvent(self.step_count, "diplomatic",
                          f"🌤️ 気象ゴリラのせい({ft}→{tt})", self.frontend)
            self._emit(ev)

    def banana_gc(self, n: int):
        erased_count = len(self._history)
        # ③ HistoryRewriteEvent: 消した事件を記録
        for old_ev in list(self._history):
            hrev = HistoryRewriteEvent(
                step=self.step_count, kind="history_rewrite",
                detail=f"🍌×{n}で歴史改変", frontend=self.frontend,
                erased_event=old_ev.detail,
                rewritten_as="最初から存在しなかったことになった",
            )
            self._erased_events.append(hrev)
        self._history.clear()
        ev = CivEvent(self.step_count, "banana_gc",
                      f"🍌×{n} → {erased_count}件歴史消滅", self.frontend)
        self._events.append(ev)  # GC自体は消えない（メタ歴史）
        return erased_count

    def snapshot_kont(self, step_no: int, k: Kont):
        """② Kont木スナップショット"""
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
# § 5  CEK洞窟マシン（CivilizationSink対応）
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
        if isinstance(e, OdorLevelExpr):          # ① 最適化済み直値
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
            raise 哲学ゴリラ例外(e.question)
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
# § 6  TraceCollector + RunCapture（Kont木スナップショット付き）
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

KONT_SNAP_STEPS = {0, 1, 5, 10, 20}  # ② Kontスナップを取るステップ

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
        # ② Kont木スナップショット
        if step_no in KONT_SNAP_STEPS:
            kont_snaps.append(KontSnapshot(step_no, kont_to_tree(state.kont), frontend))
        try:
            state = step(state)
        except ScatError as e:
            return RunCapture(None, col, make_error(step_no, state, e), sink, kont_snaps), opt_report

    exc = StepLimitError(f"step limit exceeded: {max_steps}")
    return RunCapture(None, col, make_error(max_steps, state, exc), sink, kont_snaps), opt_report

# ══════════════════════════════════════════════════════════════
# § 7  ④ マンモス分散トランザクション — Ghost Odor
#       洞窟A成功 + 洞窟B失敗 → 臭いだけ存在・犯人不在
# ══════════════════════════════════════════════════════════════

def mammoth_distributed_transaction(cave_a_prog, cave_b_prog,
                                    fe_a="🦣CaveA", fe_b="🦣CaveB"):
    """
    取引 {
        洞窟A.排出()   # 成功
        洞窟B.観測()   # 失敗
    }
    → Ghost Odor: 臭いだけ存在・犯人不在
    """
    # Phase 1: Prepare
    print(f"\n  [2Phase] Prepare...")
    cap_a, _ = run_capture(cave_a_prog, frontend=fe_a)
    cap_b, _ = run_capture(cave_b_prog, frontend=fe_b)

    a_ok = cap_a.ok()
    b_ok = cap_b.ok()
    print(f"  {fe_a}: {'✅ 成功' if a_ok else '❌ 失敗'}")
    print(f"  {fe_b}: {'✅ 成功' if b_ok else '❌ 失敗'}")

    if a_ok and not b_ok:
        # Ghost Odor 発生！
        odor_events = cap_a.sink.events
        odor_level  = sum(1 for e in odor_events if e.kind == "odor")
        ghost = GhostOdorEvent(
            step=cap_b.error.step if cap_b.error else 0,
            kind="ghost_odor",
            detail=f"👻 Ghost Odor Lv{odor_level}: 臭いだけ存在・犯人不在",
            frontend=f"{fe_a}+{fe_b}",
            cave_a=fe_a, cave_b=fe_b, odor_level=odor_level,
        )
        print(f"\n  💀 Ghost Odor 発生！")
        print(f"     {ghost.detail}")
        print(f"     原因: {fe_a}が排出したが{fe_b}がロールバック")
        print(f"     → 臭気は世界に存在する。しかし誰も認めない。")
        return ghost
    elif a_ok and b_ok:
        print(f"\n  ✅ 両洞窟コミット成功")
        return None
    else:
        print(f"\n  ⚠️  両洞窟ロールバック（臭気なし）")
        return None

# ══════════════════════════════════════════════════════════════
# § 8  ⑥ ゴリラ不完全性定理
# ══════════════════════════════════════════════════════════════

class GorillaTheoremProver:
    """
    証明: おなら = 風  → 証明失敗（理由: 観測者が存在する）
    証明: おなら ≠ 風  → 証明失敗（理由: 風向きが不明）
    → ゴリラ不完全性定理: どっちも証明できない
    """

    axioms = {
        "おならは観測されるまで風である": True,
        "焼き芋は副作用を隠蔽しない": True,
        "純粋関数は臭わない": True,
        "臭った時点で世界は変更済み": True,
    }

    @classmethod
    def prove(cls, statement: str) -> dict:
        if statement == "おなら = 風":
            return {
                "statement": statement,
                "result": "証明失敗",
                "reason": "観測者が存在する（観測した瞬間に状態が確定し、風の可能性が崩壊するウホ）",
                "theorem": "ゴリラ不完全性定理 補題1",
            }
        elif statement == "おなら ≠ 風":
            return {
                "statement": statement,
                "result": "証明失敗",
                "reason": "風向きが不明（気象ゴリラが証言を拒否したウホ）",
                "theorem": "ゴリラ不完全性定理 補題2",
            }
        elif statement == "おなら ∈ {風, おなら}":
            return {
                "statement": statement,
                "result": "証明失敗",
                "reason": "集合の定義が哲学ゴリラに破壊された",
                "theorem": "ゴリラ不完全性定理 補題3",
            }
        else:
            return {
                "statement": statement,
                "result": "証明失敗",
                "reason": "哲学ゴリラが問いを食べたウホ",
                "theorem": "ゴリラ不完全性定理 一般形",
            }

    @classmethod
    def print_theorem(cls):
        print("""
  ┌─────────────────────────────────────────────────────┐
  │  ゴリラ不完全性定理（Gorilla Incompleteness Theorem）│
  │                                                     │
  │  系 1: おなら = 風  は証明不可能                    │
  │  系 2: おなら ≠ 風  も証明不可能                    │
  │  系 3: この定理自体も証明不可能                     │
  │                                                     │
  │  ∀ 命題 P ∈ DungLang :                            │
  │    prove(P) = 証明失敗  ∨  prove(¬P) = 証明失敗   │
  │                                                     │
  │  ただし焼き芋補正により真実度+12%                   │
  └─────────────────────────────────────────────────────┘""")

# ══════════════════════════════════════════════════════════════
# § 9  ★ Replay Civilization
#       全イベントを時系列で再生するウホ📜
# ══════════════════════════════════════════════════════════════

def replay_civilization(all_events: list):
    print("""
  ══════════════════════════════════════════
   📜 Replay Civilization
   文明の全歴史を再生するウホ
  ══════════════════════════════════════════""")

    by_step = sorted(all_events, key=lambda e: e.step)
    for ev in by_step:
        if isinstance(ev, HistoryRewriteEvent):
            print(f"  step {ev.step:>4} | 📜🔥 歴史改変")
            print(f"           消滅: 「{ev.erased_event}」")
            print(f"           → {ev.rewritten_as}")
        elif isinstance(ev, GhostOdorEvent):
            print(f"  step {ev.step:>4} | 👻 Ghost Odor Lv{ev.odor_level}")
            print(f"           {ev.cave_a}→{ev.cave_b}: 臭いだけ世界に残った")
        else:
            icon = {
                "odor": "💨", "diplomatic": "🌍", "banana_gc": "🍌",
                "observe": "👁️", "history_rewrite": "📜",
            }.get(ev.kind, "・")
            print(f"  step {ev.step:>4} | {icon} [{ev.frontend}] {ev.detail}")

    print(f"\n  総イベント数: {len(all_events)}")

# ══════════════════════════════════════════════════════════════
# § 10  メイン
# ══════════════════════════════════════════════════════════════

def banner(t): print(f"\n{'━'*64}\n  {t}\n{'━'*64}")
TRUE_VAL  = PoopSucc(PoopZero())

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    banner("DungLang Civilization v2.0  🦍🔥🍌💨🌍📜")
    print("  DungLang = 世界観 | MysticIR = 検証エンジン | Federation = 文明シミュレータ")

    all_civ_events = []   # ★ 全文明イベントを集める

    # ────────────────────────────────────────────────────────
    # ① 臭気IR最適化器
    # ────────────────────────────────────────────────────────
    banner("① 臭気IR最適化器 — 💨+💨+💨+💨 → OdorLevel(4)")

    # 非最適化: PoopSucc連打で4
    prog_unopt = (
        Assign("x", int_to_expr(4)),   # SuccSuccSuccSuccZero
        OdorFlush(Var("x"), source="マンモス"),
    )
    prog_opt, opt_rep = optimize_program(prog_unopt)

    print(f"\n  最適化前 ノード数: {opt_rep.original_nodes}")
    print(f"  最適化後 ノード数: {opt_rep.optimized_nodes}")
    print(f"  畳み込み削減:     {opt_rep.folded_odor} ノード削減")
    for s in prog_opt:
        print(f"  最適化済みStmt: {s}")

    # 哲学版
    prog_phil = (
        Assign("q1", PhilosophyExpr("おならとは何か")),
        Assign("q2", PhilosophyExpr("風とは何か")),
        Assign("q3", PhilosophyExpr("存在とは何か")),
    )
    _, opt_phil = optimize_program(prog_phil)
    print(f"\n  哲学呼び出し: {opt_phil.philosophy_calls}回")
    print(f"  → 公理破壊確率: {opt_phil.axiom_break_prob:.1f}%  ⚠️  危険ウホ！")

    # 実行（最適化あり）
    cap, orep = run_capture(prog_unopt, frontend="💩ScatLang", optimize=True)
    if cap.ok():
        for ev in cap.sink.events:
            print(f"  実行イベント: {ev.detail}")
            all_civ_events.append(ev)

    # ────────────────────────────────────────────────────────
    # ② Kont Federation — 継続木の同一性証明
    # ────────────────────────────────────────────────────────
    banner("② Kont Federation — 継続木の同一性証明")

    common = (
        Assign("x", int_to_expr(3)),
        Assign("y", int_to_expr(2)),
        Flush(OdorAdd(Var("x"), Var("y"))),
    )

    cap_scat, _ = run_capture(common, frontend="💩ScatLang")
    cap_sea,  _ = run_capture(common, frontend="🌊SeaIR")

    # Kont木スナップショット比較
    print(f"\n  ScatLang Kont木スナップショット ({len(cap_scat.kont_snapshots)}件):")
    for snap in cap_scat.kont_snapshots[:3]:
        print(f"    step {snap.step}:")
        print(snap.tree.pretty(3))

    # 同一性チェック
    scat_sigs = [s.signature() for s in cap_scat.kont_snapshots]
    sea_sigs  = [s.signature() for s in cap_sea.kont_snapshots]
    # step と tree だけ比較（frontend除く）
    scat_tree_sigs = [(s, t.signature()) for s, t in
                      [(snap.step, snap.tree) for snap in cap_scat.kont_snapshots]]
    sea_tree_sigs  = [(s, t.signature()) for s, t in
                      [(snap.step, snap.tree) for snap in cap_sea.kont_snapshots]]
    kont_equal = scat_tree_sigs == sea_tree_sigs
    print(f"\n  Kont木 同一性: {'✅ 同一ウホ！' if kont_equal else '❌ 差異あり'}")
    print(f"  （地上の宗教が違っても、継続の形まで同じウホ🪨）")

    # ────────────────────────────────────────────────────────
    # ③ History Federation — 歴史が書き換わる
    # ────────────────────────────────────────────────────────
    banner("③ History Federation — バナナで歴史を消すウホ📜🍌")

    sink_hist = CivilizationSink(frontend="🦍DungLang")
    sink_hist.step_count = 17
    sink_hist.observe_odor(7, "マンモス")
    sink_hist.step_count = 42
    try:
        sink_hist.observe_diplomatic(7, "ウホ族", "バナナ族")
    except 越境臭気例外:
        pass
    sink_hist.step_count = 88

    print(f"\n  現在の歴史 ({len(sink_hist.live_history)}件):")
    for ev in sink_hist.live_history:
        print(f"    step {ev.step}: {ev.detail}")

    print(f"\n  🍌 バナナ3本投入...")
    erased = sink_hist.banana_gc(3)
    print(f"  {erased}件の歴史が消滅")

    print(f"\n  消された歴史 (HistoryRewriteEvent):")
    for hrev in sink_hist.erased_events:
        print(f"    「{hrev.erased_event}」→ {hrev.rewritten_as}")
        all_civ_events.append(hrev)

    print(f"  現在の公式歴史: {len(sink_hist.live_history)}件（空白）")

    # ────────────────────────────────────────────────────────
    # ④ マンモス分散トランザクション — Ghost Odor
    # ────────────────────────────────────────────────────────
    banner("④ マンモス分散トランザクション — Ghost Odor 👻")

    # 洞窟A: 臭気排出成功
    cave_a = (OdorFlush(int_to_expr(5), source="マンモス"),)
    # 洞窟B: unbound variable で失敗（ロールバック）
    cave_b = (Flush(Var("missing_observer")),)

    ghost = mammoth_distributed_transaction(cave_a, cave_b)
    if ghost:
        all_civ_events.append(ghost)

    # ────────────────────────────────────────────────────────
    # ⑥ ゴリラ不完全性定理
    # ────────────────────────────────────────────────────────
    banner("⑥ ゴリラ不完全性定理 — どっちも証明できないウホ")

    GorillaTheoremProver.print_theorem()
    print()

    for stmt in ["おなら = 風", "おなら ≠ 風", "おなら ∈ {風, おなら}"]:
        r = GorillaTheoremProver.prove(stmt)
        print(f"  証明: 「{r['statement']}」")
        print(f"    結果: {r['result']}")
        print(f"    理由: {r['reason']}")
        print(f"    ({r['theorem']})")
        print()

    # ────────────────────────────────────────────────────────
    # ★ Replay Civilization
    # ────────────────────────────────────────────────────────
    banner("★ Replay Civilization — 文明の全歴史を再生するウホ📜")

    # 追加イベント（OdorFlush実行分）
    for ev in cap.sink.events:
        if ev not in all_civ_events:
            all_civ_events.append(ev)

    replay_civilization(all_civ_events)

    # ────────────────────────────────────────────────────────
    # 総括
    # ────────────────────────────────────────────────────────
    banner("DungLang Civilization v2.0 — 完全体ウホ🦍🔥🌴💩🌊🍠📜")
    print("""
  ① 臭気IR最適化器       → 💨×4 → OdorLevel(4) 畳み込み      ✅
  ② Kont Federation       → 継続木の形まで同一証明             ✅
  ③ History Federation    → バナナで歴史改変・HistoryRewrite    ✅
  ④ Ghost Odor            → 分散トランザクション障害モデル     ✅
  ⑥ ゴリラ不完全性定理   → どっちも証明不可能                  ✅
  ★ Replay Civilization  → 文明イベントソーシング再生          ✅

  成功は同じ。失敗も同じ。
  歴史が消えても、イベントログは残る。
  ゴリラが証明しようとしても、定理が崩れる。
  これが文明ウホ。🪨🔥

  v2.1 ロードマップ:
    ⑤ 洞窟WebSocket (OdorEventをリアルタイム配信)
    v3.0 pip install dunglang 🍌🔥
""")

    # JSON保存
    out = "/mnt/user-data/outputs/dunglang_civilization_v2_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {"civilization_events": [e.to_dict() for e in all_civ_events]},
            f, ensure_ascii=False, indent=2
        )
    print(f"  レポート保存: {out}")

if __name__ == "__main__":
    main()
