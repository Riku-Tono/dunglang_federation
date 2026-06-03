# -*- coding: utf-8 -*-
"""
DungLang Civilization v2.2
===========================
GPT v2.1 + Claude追加モジュール

  v2.0 (Claude):
    - OdorOptimizer
    - Kont Federation
    - History Federation
    - Ghost Odor
    - Gorilla Incompleteness
    - Replay Civilization

  v2.1 (GPT):
    - Civilization Event Store
    - Temporal Banana Rewrite
    - Official History vs Archaeological Trace
    - Ghost Odor Archaeology
    - Civilization Federation Comparator
    - Causality Leak Detector

  v2.2 (Claude):
    - OdorTypeInference  (哲学型・外交型・汚染型を静的検出)
    - TwoPhaseCommit     (CommittedOdor/RolledBackOdor/GhostOdorを型で区別)
    - WitnessCouncil     (考古学痕跡を証人評議会で審議、哲学ゴリラ自動除外)

これは発表用・研究玩具用プロトタイプです。
完全なコンパイラ、完全証明、完全な分散トランザクション処理系ではありません。
ウホ🦍📜🔥🍌💨🌍⚗️
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Optional


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ══════════════════════════════════════════════════════════════
# §0 Exceptions / Values
# ══════════════════════════════════════════════════════════════

class ScatError(Exception):
    pass

class StepLimitError(ScatError):
    pass

class 哲学ゴリラ例外(ScatError):
    pass

class 越境臭気例外(ScatError):
    pass

class TemporalParadoxWarning(Warning):
    pass


class Value:
    def pretty(self) -> str:
        raise NotImplementedError

    def to_int(self) -> int:
        raise NotImplementedError


@dataclass(frozen=True)
class PoopZero(Value):
    def pretty(self) -> str:
        return "💩₀"

    def to_int(self) -> int:
        return 0


@dataclass(frozen=True)
class PoopSucc(Value):
    inner: Value

    def pretty(self) -> str:
        return f"💩×{self.to_int()}"

    def to_int(self) -> int:
        return 1 + self.inner.to_int()


@dataclass(frozen=True)
class Underflow(Value):
    def pretty(self) -> str:
        return "💩∅"

    def to_int(self) -> int:
        return 0


def int_to_poop(n: int) -> Value:
    if n < 0:
        raise ValueError("DungLang natural odor cannot be negative")
    v: Value = PoopZero()
    for _ in range(n):
        v = PoopSucc(v)
    return v


TRUE = PoopSucc(PoopZero())
FALSE = PoopZero()


# ══════════════════════════════════════════════════════════════
# §1 Odor IR
# ══════════════════════════════════════════════════════════════

class Expr:
    pass

class Stmt:
    pass


@dataclass(frozen=True)
class PoopZeroExpr(Expr):
    pass

@dataclass(frozen=True)
class PoopSuccExpr(Expr):
    expr: Expr

@dataclass(frozen=True)
class OdorLevelExpr(Expr):
    level: int

@dataclass(frozen=True)
class Var(Expr):
    name: str

@dataclass(frozen=True)
class OdorAdd(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class OdorSub(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class OdorNeq(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class PhilosophyExpr(Expr):
    question: str


@dataclass(frozen=True)
class Assign(Stmt):
    name: str
    expr: Expr

@dataclass(frozen=True)
class Flush(Stmt):
    expr: Expr

@dataclass(frozen=True)
class OdorFlush(Stmt):
    expr: Expr
    source: str = "不明"

@dataclass(frozen=True)
class DiplomaticFlush(Stmt):
    expr: Expr
    from_tribe: str
    to_tribe: str

@dataclass(frozen=True)
class While(Stmt):
    left: Expr
    right: Expr
    body: tuple[Stmt, ...]


def int_to_expr(n: int) -> Expr:
    e: Expr = PoopZeroExpr()
    for _ in range(n):
        e = PoopSuccExpr(e)
    return e


def expr_to_int(e: Expr) -> Optional[int]:
    if isinstance(e, PoopZeroExpr):
        return 0
    if isinstance(e, PoopSuccExpr):
        inner = expr_to_int(e.expr)
        return None if inner is None else inner + 1
    if isinstance(e, OdorLevelExpr):
        return e.level
    return None


# ══════════════════════════════════════════════════════════════
# §2 Optimizer
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class OptimizeReport:
    original_nodes: int
    optimized_nodes: int
    folded_nodes: int
    philosophy_calls: int
    axiom_break_prob: float

    def to_dict(self) -> dict:
        return {
            "original_nodes": self.original_nodes,
            "optimized_nodes": self.optimized_nodes,
            "folded_nodes": self.folded_nodes,
            "philosophy_calls": self.philosophy_calls,
            "axiom_break_prob": self.axiom_break_prob,
        }


def count_nodes(e: Expr) -> int:
    if isinstance(e, (PoopZeroExpr, OdorLevelExpr, Var, PhilosophyExpr)):
        return 1
    if isinstance(e, PoopSuccExpr):
        return 1 + count_nodes(e.expr)
    if isinstance(e, (OdorAdd, OdorSub, OdorNeq)):
        return 1 + count_nodes(e.left) + count_nodes(e.right)
    return 1


def optimize_expr(e: Expr) -> Expr:
    folded = expr_to_int(e)
    if folded is not None:
        return OdorLevelExpr(folded)

    if isinstance(e, PoopSuccExpr):
        inner = optimize_expr(e.expr)
        v = expr_to_int(inner)
        return OdorLevelExpr(v + 1) if v is not None else PoopSuccExpr(inner)

    if isinstance(e, OdorAdd):
        left = optimize_expr(e.left)
        right = optimize_expr(e.right)
        lv, rv = expr_to_int(left), expr_to_int(right)
        if lv is not None and rv is not None:
            return OdorLevelExpr(lv + rv)
        return OdorAdd(left, right)

    if isinstance(e, OdorSub):
        left = optimize_expr(e.left)
        right = optimize_expr(e.right)
        lv, rv = expr_to_int(left), expr_to_int(right)
        if lv is not None and rv is not None:
            return OdorLevelExpr(max(lv - rv, 0))
        return OdorSub(left, right)

    if isinstance(e, OdorNeq):
        return OdorNeq(optimize_expr(e.left), optimize_expr(e.right))

    return e


def count_philosophy(prog: tuple[Stmt, ...]) -> int:
    n = 0
    for stmt in prog:
        if hasattr(stmt, "expr") and isinstance(getattr(stmt, "expr"), PhilosophyExpr):
            n += 1
    return n


def optimize_program(prog: tuple[Stmt, ...]) -> tuple[tuple[Stmt, ...], OptimizeReport]:
    original_nodes = sum(count_nodes(s.expr) for s in prog if hasattr(s, "expr"))
    optimized: list[Stmt] = []

    for s in prog:
        if isinstance(s, Assign):
            optimized.append(Assign(s.name, optimize_expr(s.expr)))
        elif isinstance(s, Flush):
            optimized.append(Flush(optimize_expr(s.expr)))
        elif isinstance(s, OdorFlush):
            optimized.append(OdorFlush(optimize_expr(s.expr), s.source))
        elif isinstance(s, DiplomaticFlush):
            optimized.append(DiplomaticFlush(optimize_expr(s.expr), s.from_tribe, s.to_tribe))
        else:
            optimized.append(s)

    optimized_tuple = tuple(optimized)
    optimized_nodes = sum(count_nodes(s.expr) for s in optimized_tuple if hasattr(s, "expr"))
    phil = count_philosophy(optimized_tuple)
    report = OptimizeReport(
        original_nodes=original_nodes,
        optimized_nodes=optimized_nodes,
        folded_nodes=original_nodes - optimized_nodes,
        philosophy_calls=phil,
        axiom_break_prob=min(97.0, phil * 32.3),
    )
    return optimized_tuple, report


# ══════════════════════════════════════════════════════════════
# §3 Kont / CEK
# ══════════════════════════════════════════════════════════════

class Kont:
    pass

@dataclass(frozen=True)
class Halt(Kont):
    pass

@dataclass(frozen=True)
class AssignK(Kont):
    name: str
    rest: tuple[Stmt, ...]
    env: dict[str, Value]
    kont: Kont

@dataclass(frozen=True)
class FlushK(Kont):
    rest: tuple[Stmt, ...]
    env: dict[str, Value]
    kont: Kont

@dataclass(frozen=True)
class OdorFlushK(Kont):
    rest: tuple[Stmt, ...]
    env: dict[str, Value]
    kont: Kont
    source: str

@dataclass(frozen=True)
class DiplomaticFlushK(Kont):
    rest: tuple[Stmt, ...]
    env: dict[str, Value]
    kont: Kont
    from_tribe: str
    to_tribe: str

@dataclass(frozen=True)
class SuccK(Kont):
    kont: Kont

@dataclass(frozen=True)
class AddLeftK(Kont):
    right: Expr
    env: dict[str, Value]
    kont: Kont

@dataclass(frozen=True)
class AddRightK(Kont):
    left_val: Value
    kont: Kont

@dataclass(frozen=True)
class SubLeftK(Kont):
    right: Expr
    env: dict[str, Value]
    kont: Kont

@dataclass(frozen=True)
class SubRightK(Kont):
    left_val: Value
    kont: Kont

@dataclass(frozen=True)
class NeqLeftK(Kont):
    right: Expr
    env: dict[str, Value]
    kont: Kont

@dataclass(frozen=True)
class NeqRightK(Kont):
    left_val: Value
    kont: Kont

@dataclass(frozen=True)
class WhileK(Kont):
    stmt: While
    rest: tuple[Stmt, ...]
    env: dict[str, Value]
    kont: Kont


@dataclass(frozen=True)
class EvalExpr:
    expr: Expr

@dataclass(frozen=True)
class ReturnValue:
    value: Value


@dataclass
class State:
    control: object
    env: dict[str, Value]
    kont: Kont
    sink: "CivilizationEventStore"


def kont_depth(k: Kont) -> int:
    d = 0
    current = k
    while not isinstance(current, Halt):
        d += 1
        current = getattr(current, "kont", Halt())
    return d


@dataclass(frozen=True)
class KontTree:
    kind: str
    meta: str = ""
    child: Optional["KontTree"] = None

    def signature(self) -> tuple:
        return (self.kind, self.meta, self.child.signature() if self.child else None)

    def pretty(self, indent: int = 0) -> str:
        pad = "  " * indent
        line = f"{pad}{self.kind}"
        if self.meta:
            line += f"({self.meta})"
        return line if self.child is None else line + "\n" + self.child.pretty(indent + 1)


def kont_to_tree(k: Kont) -> KontTree:
    if isinstance(k, Halt):
        return KontTree("Halt")
    meta = ""
    if hasattr(k, "name"):
        meta = getattr(k, "name")
    if hasattr(k, "source"):
        meta = getattr(k, "source")
    return KontTree(type(k).__name__, meta, kont_to_tree(getattr(k, "kont", Halt())))


def is_halted(s: State) -> bool:
    return isinstance(s.control, ReturnValue) and isinstance(s.kont, Halt)


def poop_add(a: Value, b: Value) -> Value:
    return int_to_poop(a.to_int() + b.to_int())


def poop_sub(a: Value, b: Value) -> Value:
    return int_to_poop(max(a.to_int() - b.to_int(), 0))


def poop_neq(a: Value, b: Value) -> Value:
    return TRUE if a.to_int() != b.to_int() else FALSE


TREATY = {
    ("ウホ族", "バナナ族"): 3,
    ("ウホ族", "マンモス部族"): 5,
    ("バナナ族", "マンモス部族"): 4,
    ("哲学ゴリラ連邦", "*"): 0,
}


def step(state: State) -> State:
    state.sink.tick()
    ctrl = state.control

    if isinstance(ctrl, tuple):
        if not ctrl:
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)

        head, *tail = ctrl
        rest = tuple(tail)
        if isinstance(head, Assign):
            return State(EvalExpr(head.expr), state.env, AssignK(head.name, rest, dict(state.env), state.kont), state.sink)
        if isinstance(head, Flush):
            return State(EvalExpr(head.expr), state.env, FlushK(rest, dict(state.env), state.kont), state.sink)
        if isinstance(head, OdorFlush):
            return State(EvalExpr(head.expr), state.env, OdorFlushK(rest, dict(state.env), state.kont, head.source), state.sink)
        if isinstance(head, DiplomaticFlush):
            return State(EvalExpr(head.expr), state.env, DiplomaticFlushK(rest, dict(state.env), state.kont, head.from_tribe, head.to_tribe), state.sink)
        if isinstance(head, While):
            return State(EvalExpr(OdorNeq(head.left, head.right)), state.env, WhileK(head, rest, dict(state.env), state.kont), state.sink)
        raise ScatError(f"unknown stmt: {head!r}")

    if isinstance(ctrl, EvalExpr):
        e = ctrl.expr
        if isinstance(e, PoopZeroExpr):
            return State(ReturnValue(PoopZero()), state.env, state.kont, state.sink)
        if isinstance(e, PoopSuccExpr):
            return State(EvalExpr(e.expr), state.env, SuccK(state.kont), state.sink)
        if isinstance(e, OdorLevelExpr):
            return State(ReturnValue(int_to_poop(e.level)), state.env, state.kont, state.sink)
        if isinstance(e, Var):
            if e.name not in state.env:
                raise ScatError(f"unbound variable: {e.name}")
            return State(ReturnValue(state.env[e.name]), state.env, state.kont, state.sink)
        if isinstance(e, OdorAdd):
            return State(EvalExpr(e.left), state.env, AddLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorSub):
            return State(EvalExpr(e.left), state.env, SubLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, OdorNeq):
            return State(EvalExpr(e.left), state.env, NeqLeftK(e.right, dict(state.env), state.kont), state.sink)
        if isinstance(e, PhilosophyExpr):
            raise 哲学ゴリラ例外(e.question)
        raise ScatError(f"unknown expr: {e!r}")

    if isinstance(ctrl, ReturnValue):
        v = ctrl.value
        k = state.kont
        if isinstance(k, Halt):
            return state
        if isinstance(k, SuccK):
            return State(ReturnValue(PoopSucc(v)), state.env, k.kont, state.sink)
        if isinstance(k, AssignK):
            new_env = dict(k.env)
            new_env[k.name] = v
            return State(k.rest, new_env, k.kont, state.sink)
        if isinstance(k, FlushK):
            state.sink.observe(v, "flush")
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
        if isinstance(k, SubLeftK):
            return State(EvalExpr(k.right), dict(k.env), SubRightK(v, k.kont), state.sink)
        if isinstance(k, SubRightK):
            return State(ReturnValue(poop_sub(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, NeqLeftK):
            return State(EvalExpr(k.right), dict(k.env), NeqRightK(v, k.kont), state.sink)
        if isinstance(k, NeqRightK):
            return State(ReturnValue(poop_neq(k.left_val, v)), state.env, k.kont, state.sink)
        if isinstance(k, WhileK):
            if v.to_int() == 0:
                return State(k.rest, dict(k.env), k.kont, state.sink)
            return State(k.stmt.body + (k.stmt,) + k.rest, dict(k.env), k.kont, state.sink)
        raise ScatError(f"unknown kont: {k!r}")

    raise ScatError(f"unknown ctrl: {ctrl!r}")


# ══════════════════════════════════════════════════════════════
# §4 Civilization Events / Event Store
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CivEvent:
    step: int
    kind: str
    detail: str
    frontend: str
    era: str = "official"

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "kind": self.kind,
            "detail": self.detail,
            "frontend": self.frontend,
            "era": self.era,
        }


@dataclass(frozen=True)
class HistoryRewriteEvent(CivEvent):
    erased_event: str = ""
    rewritten_as: str = "最初から存在しなかったことになった"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "erased_event": self.erased_event,
            "rewritten_as": self.rewritten_as,
        })
        return d


@dataclass(frozen=True)
class ArchaeologicalArtifact(CivEvent):
    artifact_id: str = ""
    source_event: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "artifact_id": self.artifact_id,
            "source_event": self.source_event,
            "confidence": self.confidence,
        })
        return d


@dataclass(frozen=True)
class GhostOdorEvent(CivEvent):
    cave_a: str = ""
    cave_b: str = ""
    odor_level: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "cave_a": self.cave_a,
            "cave_b": self.cave_b,
            "odor_level": self.odor_level,
        })
        return d


@dataclass(frozen=True)
class CausalityLeakEvent(CivEvent):
    leaked_from: str = ""
    leaked_into: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"leaked_from": self.leaked_from, "leaked_into": self.leaked_into})
        return d


@dataclass
class CivilizationEventStore:
    frontend: str = "unknown"
    step_count: int = 0
    _full_log: list[CivEvent] = field(default_factory=list)
    _official_history: list[CivEvent] = field(default_factory=list)
    _archaeology: list[ArchaeologicalArtifact] = field(default_factory=list)
    _observations: list[tuple[Value, int, str]] = field(default_factory=list)
    _kont_snapshots: list[tuple[int, KontTree]] = field(default_factory=list)

    def tick(self) -> None:
        self.step_count += 1

    def emit(self, ev: CivEvent, *, official: bool = True) -> None:
        self._full_log.append(ev)
        if official:
            self._official_history.append(ev)

    def observe(self, v: Value, ctx: str = "flush") -> None:
        self._observations.append((v, self.step_count, ctx))
        self.emit(CivEvent(self.step_count, "observe", v.pretty(), self.frontend))

    def observe_odor(self, level: int, source: str) -> None:
        self.emit(CivEvent(self.step_count, "odor", f"💨 Lv{level}({source})", self.frontend))

    def observe_diplomatic(self, level: int, from_tribe: str, to_tribe: str) -> None:
        if "哲学ゴリラ" in from_tribe:
            treaty = 0
        else:
            treaty = TREATY.get((from_tribe, to_tribe), 4)
        if level > treaty:
            banana = level * 2
            ev = CivEvent(self.step_count, "diplomatic", f"🌍 {from_tribe}→{to_tribe} 濃度{level} バナナ{banana}本", self.frontend)
            self.emit(ev)
            raise 越境臭気例外(f"{from_tribe}→{to_tribe} 濃度{level} バナナ{banana}本賠償")
        self.emit(CivEvent(self.step_count, "diplomatic", f"🌤️ 気象ゴリラのせい({from_tribe}→{to_tribe})", self.frontend))

    def temporal_banana_rewrite(self, banana_count: int, *, target_kind: Optional[str] = None, max_rewrites: Optional[int] = None) -> list[HistoryRewriteEvent]:
        """公式歴史を削るが、full_log と archaeology には痕跡を残すウホ。"""
        if banana_count < 3:
            ev = CivEvent(self.step_count, "banana_failed", f"🍌×{banana_count} 歴史改変失敗", self.frontend)
            self.emit(ev)
            return []

        candidates = [ev for ev in self._official_history if target_kind is None or ev.kind == target_kind]
        if max_rewrites is not None:
            candidates = candidates[:max_rewrites]

        rewrites: list[HistoryRewriteEvent] = []
        for idx, old in enumerate(candidates, 1):
            rewrite = HistoryRewriteEvent(
                step=self.step_count,
                kind="history_rewrite",
                detail=f"🍌×{banana_count}で過去改変",
                frontend=self.frontend,
                era="meta",
                erased_event=old.detail,
                rewritten_as="最初から存在しなかったことになった",
            )
            artifact = ArchaeologicalArtifact(
                step=self.step_count,
                kind="artifact",
                detail=f"🪨 壁画痕跡: {old.detail}",
                frontend="ArchaeologyIR",
                era="archaeological",
                artifact_id=f"ART-{self.step_count}-{idx}",
                source_event=old.detail,
                confidence=max(0.12, min(0.97, 0.35 + banana_count / 20)),
            )
            rewrites.append(rewrite)
            self._full_log.append(rewrite)
            self._full_log.append(artifact)
            self._archaeology.append(artifact)

        self._official_history = [ev for ev in self._official_history if ev not in candidates]
        self._full_log.append(CivEvent(
            self.step_count,
            "banana_gc",
            f"🍌×{banana_count} → {len(candidates)}件の公式歴史を改変",
            self.frontend,
            era="meta",
        ))
        return rewrites

    def snapshot_kont(self, step_no: int, k: Kont) -> None:
        self._kont_snapshots.append((step_no, kont_to_tree(k)))

    @property
    def observations(self) -> tuple[tuple[Value, int, str], ...]:
        return tuple(self._observations)

    @property
    def full_log(self) -> list[CivEvent]:
        return list(self._full_log)

    @property
    def official_history(self) -> list[CivEvent]:
        return list(self._official_history)

    @property
    def archaeology(self) -> list[ArchaeologicalArtifact]:
        return list(self._archaeology)

    @property
    def kont_snapshots(self) -> list[tuple[int, KontTree]]:
        return list(self._kont_snapshots)


# ══════════════════════════════════════════════════════════════
# §5 Trace / Run Capture
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TraceEvent:
    step: int
    control_kind: str
    expr_kind: str
    kont_kind: str
    kont_depth: int
    env_keys: tuple[str, ...]
    observed_count: int
    frontend: str

    def signature(self, *, include_frontend: bool = False) -> tuple:
        base = (self.control_kind, self.expr_kind, self.kont_kind, self.kont_depth, self.env_keys, self.observed_count)
        return base + ((self.frontend,) if include_frontend else ())

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "control_kind": self.control_kind,
            "expr_kind": self.expr_kind,
            "kont_kind": self.kont_kind,
            "kont_depth": self.kont_depth,
            "env_keys": list(self.env_keys),
            "observed_count": self.observed_count,
            "frontend": self.frontend,
        }


@dataclass(frozen=True)
class TraceErrorEvent:
    step: int
    control_kind: str
    expr_kind: str
    kont_kind: str
    kont_depth: int
    env_keys: tuple[str, ...]
    observed_count: int
    frontend: str
    error_type: str
    error_message: str

    def signature(self, *, include_frontend: bool = False) -> tuple:
        base = (self.control_kind, self.expr_kind, self.kont_kind, self.kont_depth, self.env_keys, self.observed_count, self.error_type, self.error_message)
        return base + ((self.frontend,) if include_frontend else ())

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "control_kind": self.control_kind,
            "expr_kind": self.expr_kind,
            "kont_kind": self.kont_kind,
            "kont_depth": self.kont_depth,
            "env_keys": list(self.env_keys),
            "observed_count": self.observed_count,
            "frontend": self.frontend,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }


class TraceCollector:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def __call__(self, ev: TraceEvent) -> None:
        self.events.append(ev)

    def signature(self, *, include_frontend: bool = False) -> tuple[tuple, ...]:
        return tuple(ev.signature(include_frontend=include_frontend) for ev in self.events)


@dataclass
class RunCapture:
    final_state: Optional[State]
    trace: TraceCollector
    error: Optional[TraceErrorEvent]
    sink: CivilizationEventStore
    optimize_report: Optional[OptimizeReport] = None

    def ok(self) -> bool:
        return self.error is None


def make_trace(step_no: int, state: State) -> TraceEvent:
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
        step=step_no,
        control_kind=ck,
        expr_kind=ek,
        kont_kind=type(state.kont).__name__,
        kont_depth=kont_depth(state.kont),
        env_keys=tuple(sorted(state.env.keys())),
        observed_count=len(state.sink.observations),
        frontend=state.sink.frontend,
    )


def make_error(step_no: int, state: State, exc: Exception) -> TraceErrorEvent:
    t = make_trace(step_no, state)
    return TraceErrorEvent(
        step=t.step,
        control_kind=t.control_kind,
        expr_kind=t.expr_kind,
        kont_kind=t.kont_kind,
        kont_depth=t.kont_depth,
        env_keys=t.env_keys,
        observed_count=t.observed_count,
        frontend=t.frontend,
        error_type=type(exc).__name__,
        error_message=str(exc),
    )


KONT_SNAPSHOT_STEPS = {0, 1, 3, 5, 8, 13, 21}


def run_capture(
    program: tuple[Stmt, ...],
    *,
    frontend: str,
    env: Optional[dict[str, Value]] = None,
    max_steps: int = 200_000,
    optimize: bool = False,
) -> RunCapture:
    optimize_report = None
    prog = tuple(program)
    if optimize:
        prog, optimize_report = optimize_program(prog)

    collector = TraceCollector()
    sink = CivilizationEventStore(frontend=frontend)
    state = State(tuple(prog), dict(env or {}), Halt(), sink)

    for step_no in range(max_steps):
        if is_halted(state):
            return RunCapture(state, collector, None, sink, optimize_report)

        collector(make_trace(step_no, state))
        if step_no in KONT_SNAPSHOT_STEPS:
            sink.snapshot_kont(step_no, state.kont)

        try:
            state = step(state)
        except ScatError as exc:
            return RunCapture(None, collector, make_error(step_no, state, exc), sink, optimize_report)

    exc = StepLimitError(f"step limit exceeded: {max_steps}")
    return RunCapture(None, collector, make_error(max_steps, state, exc), sink, optimize_report)


# ══════════════════════════════════════════════════════════════
# §6 Federation utilities
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederationReport:
    case: str
    trace_equal: bool
    surface_diff: bool
    left_frontend: str
    right_frontend: str
    left_steps: int
    right_steps: int
    left_error: Optional[dict]
    right_error: Optional[dict]
    kont_equal: bool

    def to_dict(self) -> dict:
        return {
            "case": self.case,
            "trace_equal": self.trace_equal,
            "surface_diff": self.surface_diff,
            "left_frontend": self.left_frontend,
            "right_frontend": self.right_frontend,
            "left_steps": self.left_steps,
            "right_steps": self.right_steps,
            "left_error": self.left_error,
            "right_error": self.right_error,
            "kont_equal": self.kont_equal,
        }


def paired_report(case: str, left: tuple[Stmt, ...], lf: str, right: tuple[Stmt, ...], rf: str, *, max_steps: int = 200_000) -> FederationReport:
    lcap = run_capture(left, frontend=lf, max_steps=max_steps)
    rcap = run_capture(right, frontend=rf, max_steps=max_steps)
    lks = [(step, tree.signature()) for step, tree in lcap.sink.kont_snapshots]
    rks = [(step, tree.signature()) for step, tree in rcap.sink.kont_snapshots]
    return FederationReport(
        case=case,
        trace_equal=lcap.trace.signature() == rcap.trace.signature(),
        surface_diff=lcap.trace.signature(include_frontend=True) != rcap.trace.signature(include_frontend=True),
        left_frontend=lf,
        right_frontend=rf,
        left_steps=len(lcap.trace.events),
        right_steps=len(rcap.trace.events),
        left_error=lcap.error.to_dict() if lcap.error else None,
        right_error=rcap.error.to_dict() if rcap.error else None,
        kont_equal=lks == rks,
    )


# ══════════════════════════════════════════════════════════════
# §7 Ghost Odor / Archaeology
# ══════════════════════════════════════════════════════════════

def mammoth_distributed_transaction() -> tuple[GhostOdorEvent, list[ArchaeologicalArtifact]]:
    cave_a_prog = (OdorFlush(OdorLevelExpr(5), source="マンモス"),)
    cave_b_prog = (Flush(Var("missing_observer")),)

    cap_a = run_capture(cave_a_prog, frontend="🦣CaveA")
    cap_b = run_capture(cave_b_prog, frontend="🦣CaveB")

    odor_count = sum(1 for ev in cap_a.sink.full_log if ev.kind == "odor")
    step_no = cap_b.error.step if cap_b.error else 0

    ghost = GhostOdorEvent(
        step=step_no,
        kind="ghost_odor",
        detail=f"👻 Ghost Odor Lv{odor_count}: 臭いだけ存在・犯人不在",
        frontend="🦣CaveA+🦣CaveB",
        era="liminal",
        cave_a="🦣CaveA",
        cave_b="🦣CaveB",
        odor_level=odor_count,
    )

    artifacts = [
        ArchaeologicalArtifact(
            step=step_no,
            kind="artifact",
            detail="🪨 洞窟A壁画: マンモスが何かをした形跡",
            frontend="ArchaeologyIR",
            era="archaeological",
            artifact_id="GHOST-A-001",
            source_event=ghost.detail,
            confidence=0.72,
        ),
        ArchaeologicalArtifact(
            step=step_no,
            kind="artifact",
            detail="🪨 洞窟B壁画: 観測者 missing_observer と記録",
            frontend="ArchaeologyIR",
            era="archaeological",
            artifact_id="GHOST-B-001",
            source_event=ghost.detail,
            confidence=0.64,
        ),
    ]
    return ghost, artifacts


# ══════════════════════════════════════════════════════════════
# §8 Gorilla Incompleteness Theorem
# ══════════════════════════════════════════════════════════════

class GorillaTheoremProver:
    @staticmethod
    def prove(statement: str) -> dict:
        table = {
            "おなら = 風": ("証明失敗", "観測者が存在するため、観測した瞬間に風ではなく事件になる"),
            "おなら ≠ 風": ("証明失敗", "風向きが未束縛変数で、気象ゴリラが証言を拒否した"),
            "この定理は証明可能": ("証明失敗", "定理が自分自身の臭気を観測してしまう"),
        }
        result, reason = table.get(statement, ("証明失敗", "哲学ゴリラが問いを食べた"))
        return {
            "statement": statement,
            "result": result,
            "reason": reason,
            "theorem": "ゴリラ不完全性定理 v2.2",
        }


# ══════════════════════════════════════════════════════════════
# §9 Replay / Diff
# ══════════════════════════════════════════════════════════════

def replay(events: list[CivEvent]) -> None:
    print("\n📜 Replay Civilization v2.2")
    for ev in sorted(events, key=lambda x: (x.step, x.kind, x.detail)):
        if isinstance(ev, HistoryRewriteEvent):
            print(f"  step {ev.step:>3} | 📜🔥 歴史改変: {ev.erased_event} → {ev.rewritten_as}")
        elif isinstance(ev, ArchaeologicalArtifact):
            print(f"  step {ev.step:>3} | 🪨 Artifact {ev.artifact_id}: {ev.detail} confidence={ev.confidence:.2f}")
        elif isinstance(ev, GhostOdorEvent):
            print(f"  step {ev.step:>3} | 👻 {ev.detail}")
        elif isinstance(ev, CausalityLeakEvent):
            print(f"  step {ev.step:>3} | 🌀 Causality Leak: {ev.leaked_from} → {ev.leaked_into}")
        else:
            icon = {
                "odor": "💨",
                "diplomatic": "🌍",
                "observe": "👁️",
                "banana_gc": "🍌",
                "banana_failed": "🍌",
                "theorem": "🦍",
            }.get(ev.kind, "・")
            print(f"  step {ev.step:>3} | {icon} [{ev.frontend}] {ev.detail}")


def civilization_diff(store: CivilizationEventStore) -> dict:
    official = [ev.detail for ev in store.official_history]
    archaeology = [ev.detail for ev in store.archaeology]
    full = [ev.detail for ev in store.full_log]
    missing_from_official = [ev.detail for ev in store.full_log if ev.kind in {"history_rewrite", "artifact"} or ev.detail not in official]
    return {
        "official_history_count": len(official),
        "archaeological_artifact_count": len(archaeology),
        "full_log_count": len(full),
        "missing_from_official": missing_from_official,
    }


# ══════════════════════════════════════════════════════════════
# §10 Demo programs
# ══════════════════════════════════════════════════════════════

def common_success_prog() -> tuple[Stmt, ...]:
    return (
        Assign("x", int_to_expr(3)),
        Assign("y", int_to_expr(2)),
        Flush(OdorAdd(Var("x"), Var("y"))),
    )


def philosophy_prog() -> tuple[Stmt, ...]:
    return (
        Assign("q", PhilosophyExpr("おならとは誰のものか")),
        Flush(Var("q")),
    )


def civilization_crisis_prog() -> tuple[Stmt, ...]:
    return (
        OdorFlush(int_to_expr(7), source="マンモス"),
        DiplomaticFlush(int_to_expr(7), "ウホ族", "バナナ族"),
    )


# ══════════════════════════════════════════════════════════════
# §11 Main
# ══════════════════════════════════════════════════════════════

def banner(title: str) -> None:
    print("\n" + "━" * 72)
    print(f"  {title}")
    print("━" * 72)



# ══════════════════════════════════════════════════════════════
# Claude v2.2 追加モジュール (⑦⑧⑨)
# ══════════════════════════════════════════════════════════════
import random
from enum import Enum, auto


# ══════════════════════════════════════════════════════════════
# ⑦  OdorTypeInference — 臭気型推論器
# ══════════════════════════════════════════════════════════════

class OdorType(Enum):
    PURE       = auto()
    SUSPECT    = auto()
    PHILOSOPHY = auto()
    DIPLOMATIC = auto()
    TAINTED    = auto()

    def pretty(self) -> str:
        return {
            OdorType.PURE:       "純粋(副作用なし)",
            OdorType.SUSPECT:    "疑値(副作用の可能性)",
            OdorType.PHILOSOPHY: "哲学型(証明不能)",
            OdorType.DIPLOMATIC: "外交型(越境リスク)",
            OdorType.TAINTED:    "汚染型(複合副作用)",
        }[self]


@dataclass
class TypeEnv:
    bindings: dict = field(default_factory=dict)
    def set(self, name, t): self.bindings[name] = t
    def get(self, name): return self.bindings.get(name, OdorType.PURE)
    def copy(self): return TypeEnv(dict(self.bindings))


@dataclass(frozen=True)
class TypeError_:
    var: str; expected: OdorType; got: OdorType; reason: str


@dataclass
class TypeInferenceResult:
    env: TypeEnv
    errors: list
    warnings: list

    def ok(self): return len(self.errors) == 0

    def summary(self):
        lines = ["  臭気型推論結果:"]
        for var, t in self.env.bindings.items():
            lines.append(f"    {var}: {t.pretty()}")
        for w in self.warnings:
            lines.append(f"    ⚠️  {w}")
        if self.errors:
            for e in self.errors:
                lines.append(f"    ❌ {e.var}: expected {e.expected.pretty()} got {e.got.pretty()} — {e.reason}")
        else:
            lines.append("    ✅ 型チェック通過ウホ")
        return "\n".join(lines)


def infer_expr_type(e: Expr, env: TypeEnv) -> OdorType:
    if isinstance(e, (PoopZeroExpr, OdorLevelExpr)): return OdorType.PURE
    if isinstance(e, PoopSuccExpr): return infer_expr_type(e.expr, env)
    if isinstance(e, Var): return env.get(e.name)
    if isinstance(e, PhilosophyExpr): return OdorType.PHILOSOPHY
    if isinstance(e, (OdorAdd, OdorSub)):
        lt = infer_expr_type(e.left, env)
        rt = infer_expr_type(e.right, env)
        for t in [OdorType.PHILOSOPHY, OdorType.DIPLOMATIC, OdorType.TAINTED, OdorType.SUSPECT]:
            if t in (lt, rt): return t
        return OdorType.PURE
    if isinstance(e, OdorNeq): return OdorType.PURE
    return OdorType.PURE


def infer_program(prog) -> TypeInferenceResult:
    env = TypeEnv(); errors = []; warnings = []
    for stmt in prog:
        if isinstance(stmt, Assign):
            t = infer_expr_type(stmt.expr, env); env.set(stmt.name, t)
            if t == OdorType.PHILOSOPHY:
                warnings.append(f"{stmt.name} に哲学型を代入。実行時公理破壊の恐れウホ。")
        elif isinstance(stmt, Flush):
            t = infer_expr_type(stmt.expr, env)
            if t == OdorType.PHILOSOPHY:
                errors.append(TypeError_("flush", OdorType.PURE, t, "哲学型をflushすると観測者が存在してしまう"))
            elif t == OdorType.TAINTED:
                warnings.append("汚染型の値をflushしています。副作用の連鎖に注意ウホ。")
        elif isinstance(stmt, OdorFlush):
            t = infer_expr_type(stmt.expr, env)
            if t not in (OdorType.PURE, OdorType.SUSPECT):
                warnings.append(f"OdorFlush: {t.pretty()} な値を臭気として排出。追跡が必要ウホ。")
        elif isinstance(stmt, DiplomaticFlush):
            t = infer_expr_type(stmt.expr, env)
            env.set("__diplomatic__", OdorType.DIPLOMATIC)
            if t == OdorType.PHILOSOPHY:
                errors.append(TypeError_("diplomatic", OdorType.PURE, t, "哲学型を外交に使うと条約が成立しない"))
    return TypeInferenceResult(env, errors, warnings)


# ══════════════════════════════════════════════════════════════
# ⑧  TwoPhaseCommit — マンモス2相コミット
# ══════════════════════════════════════════════════════════════

class CommitStatus(Enum):
    PREPARED    = "PREPARED"
    COMMITTED   = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    GHOST       = "GHOST"


@dataclass
class PhaseLog:
    cave: str; phase: str; status: CommitStatus; step: int; detail: str
    def to_dict(self):
        return {"cave": self.cave, "phase": self.phase, "status": self.status.value,
                "step": self.step, "detail": self.detail}


@dataclass
class TwoPhaseResult:
    cave_a: str; cave_b: str; odor_level: int
    logs: list; final_status: CommitStatus
    ghost_event: object = None
    artifacts: list = field(default_factory=list)

    def to_dict(self):
        return {
            "cave_a": self.cave_a, "cave_b": self.cave_b,
            "odor_level": self.odor_level,
            "final_status": self.final_status.value,
            "logs": [l.to_dict() for l in self.logs],
            "ghost_event": self.ghost_event.to_dict() if self.ghost_event else None,
            "artifacts": [a.to_dict() for a in self.artifacts],
        }


def mammoth_2pc(cave_a_prog, cave_b_prog, *, fe_a="🦣CaveA", fe_b="🦣CaveB"):
    import re as _re
    logs = []; odor_level = 0
    print(f"\n  [2PC Phase 1: Prepare]")
    cap_a = run_capture(cave_a_prog, frontend=fe_a)
    cap_b = run_capture(cave_b_prog, frontend=fe_b)
    a_ok = cap_a.ok(); b_ok = cap_b.ok()

    for ev in cap_a.sink.full_log:
        if ev.kind == "odor":
            m = _re.search(r"Lv(\d+)", ev.detail)
            if m: odor_level = int(m.group(1))

    logs.append(PhaseLog(fe_a, "Prepare", CommitStatus.PREPARED if a_ok else CommitStatus.ROLLED_BACK, 1,
                         "OK" if a_ok else (cap_a.error.error_message if cap_a.error else "?")))
    logs.append(PhaseLog(fe_b, "Prepare", CommitStatus.PREPARED if b_ok else CommitStatus.ROLLED_BACK, 1,
                         "OK" if b_ok else (cap_b.error.error_message if cap_b.error else "?")))
    print(f"    {fe_a}: {'✅ PREPARED' if a_ok else '❌ FAILED'}")
    print(f"    {fe_b}: {'✅ PREPARED' if b_ok else '❌ FAILED'}")
    print(f"\n  [2PC Phase 2: Commit/Rollback]")

    if a_ok and b_ok:
        logs.append(PhaseLog(fe_a, "Commit", CommitStatus.COMMITTED, 2, f"CommittedOdor Lv{odor_level}"))
        logs.append(PhaseLog(fe_b, "Commit", CommitStatus.COMMITTED, 2, "観測確定"))
        print(f"    ✅ CommittedOdor Lv{odor_level} — 臭気は世界に刻まれたウホ🪨")
        return TwoPhaseResult(fe_a, fe_b, odor_level, logs, CommitStatus.COMMITTED)

    elif a_ok and not b_ok:
        step_no = cap_b.error.step if cap_b.error else 0
        logs.append(PhaseLog(fe_a, "Commit",   CommitStatus.COMMITTED,   2, f"CommittedOdor Lv{odor_level}"))
        logs.append(PhaseLog(fe_b, "Rollback", CommitStatus.ROLLED_BACK, 2, "RolledBackOdor"))
        logs.append(PhaseLog("Coordinator", "Ghost", CommitStatus.GHOST, 2, "Ghost Odor確定"))
        ghost = GhostOdorEvent(step=step_no, kind="ghost_odor",
            detail=f"👻 Ghost Odor Lv{odor_level}: {fe_a}コミット済み・{fe_b}ロールバック",
            frontend=f"{fe_a}+{fe_b}", era="liminal",
            cave_a=fe_a, cave_b=fe_b, odor_level=odor_level)
        arts = [
            ArchaeologicalArtifact(step=step_no, kind="artifact",
                detail=f"🪨 2PC壁画: {fe_a}の排出痕跡（コミット済み）",
                frontend="ArchaeologyIR", era="archaeological",
                artifact_id=f"2PC-A-{step_no}", source_event=ghost.detail, confidence=0.91),
            ArchaeologicalArtifact(step=step_no, kind="artifact",
                detail=f"🪨 2PC壁画: {fe_b}のロールバック痕跡",
                frontend="ArchaeologyIR", era="archaeological",
                artifact_id=f"2PC-B-{step_no}", source_event=ghost.detail, confidence=0.68),
        ]
        print(f"    💀 Ghost Odor! {fe_a}=CommittedOdor Lv{odor_level}, {fe_b}=RolledBackOdor")
        return TwoPhaseResult(fe_a, fe_b, odor_level, logs, CommitStatus.GHOST, ghost, arts)

    else:
        logs.append(PhaseLog(fe_a, "Rollback", CommitStatus.ROLLED_BACK, 2, "Clean"))
        logs.append(PhaseLog(fe_b, "Rollback", CommitStatus.ROLLED_BACK, 2, "Clean"))
        print(f"    ✅ 両洞窟ロールバック（臭気ゼロ・クリーン）")
        return TwoPhaseResult(fe_a, fe_b, 0, logs, CommitStatus.ROLLED_BACK)


# ══════════════════════════════════════════════════════════════
# ⑨  WitnessCouncil — 証人評議会
# ══════════════════════════════════════════════════════════════

class ArtifactVerdict(Enum):
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    SEALED   = "SEALED"


@dataclass
class WitnessVote:
    witness: str; vote: str; reason: str; weight: float
    def to_dict(self):
        return {"witness": self.witness, "vote": self.vote, "reason": self.reason, "weight": self.weight}


@dataclass
class CouncilResult:
    artifact_id: str; original_confidence: float
    adjusted_confidence: float; verdict: ArtifactVerdict
    votes: list; council_note: str

    def to_dict(self):
        return {
            "artifact_id": self.artifact_id,
            "original_confidence": round(self.original_confidence, 3),
            "adjusted_confidence": round(self.adjusted_confidence, 3),
            "verdict": self.verdict.value,
            "votes": [v.to_dict() for v in self.votes],
            "council_note": self.council_note,
        }


WITNESS_TABLE = [
    ("研究ゴリラ", 1.0, ["odor", "artifact", "ghost_odor"]),
    ("気象ゴリラ", 1.0, ["odor", "diplomatic"]),
    ("法務ゴリラ", 2.0, ["diplomatic", "ghost_odor", "causality_leak"]),
]
PHILOSOPHY_GORILLA_EXCUSE = "🚫 哲学ゴリラ: 自動除外（前科: 無限ループ×3、バナナ没収済み）"


def witness_council_review(artifact: ArchaeologicalArtifact, seed=None) -> CouncilResult:
    rng = random.Random(seed or hash(artifact.artifact_id))
    votes = []; wtrust = 0.0; wtotal = 0.0

    for name, weight, domains in WITNESS_TABLE:
        expert = artifact.kind in domains or any(d in artifact.detail for d in domains)
        if expert:
            score = artifact.confidence + rng.uniform(-0.08, 0.12)
        else:
            score = rng.uniform(0.3, 0.7)
        score = max(0.0, min(1.0, score))
        if score >= 0.65:   vote, reason = "信頼", f"証拠と一致（{score:.2f}）"
        elif score >= 0.4:  vote, reason = "保留", f"要追加調査（{score:.2f}）"
        else:               vote, reason = "疑義", f"証拠不十分（{score:.2f}）"
        votes.append(WitnessVote(name, vote, reason, weight))
        wtrust += score * weight; wtotal += weight

    votes.append(WitnessVote("哲学ゴリラ", "除外", PHILOSOPHY_GORILLA_EXCUSE, 0.0))
    adj = max(0.0, min(1.0, wtrust / wtotal)) if wtotal > 0 else 0.0

    if adj >= 0.70:   verdict, note = ArtifactVerdict.VERIFIED, "多数の証人が信頼。公式考古学記録に採用ウホ。"
    elif adj >= 0.45: verdict, note = ArtifactVerdict.DISPUTED, "証人の意見が割れている。引き続き追跡ウホ。"
    else:             verdict, note = ArtifactVerdict.SEALED,   "信頼度が低すぎる。石板に封印ウホ。"

    return CouncilResult(artifact.artifact_id, artifact.confidence, adj, verdict, votes, note)


def council_review_all(artifacts) -> list:
    return [witness_council_review(a) for a in artifacts]


# ══════════════════════════════════════════════════════════════
# v2.2 Main
# ══════════════════════════════════════════════════════════════

def banner(t):
    print(f"\n{'━'*72}\n  {t}\n{'━'*72}")


def main() -> None:
    banner("DungLang Civilization v2.2 🦍📜🔥⚗️")
    print("  GPT v2.1 全機能継承 + Claude追加: OdorTypeInference / 2PC / WitnessCouncil")

    # ─ GPT v2.1 全セクション ─
    banner("① OdorOptimizer (GPT v2.1)")
    unopt = (Assign("x", OdorAdd(int_to_expr(2), int_to_expr(2))), OdorFlush(Var("x"), source="マンモス"))
    opt_prog, opt_report = optimize_program(unopt)
    print(f"  original={opt_report.original_nodes} → optimized={opt_report.optimized_nodes} (折畳み{opt_report.folded_nodes}ノード)")

    banner("② Federation Comparator (GPT v2.1)")
    fed_s = paired_report("common success", common_success_prog(), "💩ScatLang", common_success_prog(), "🌊SeaIR")
    fed_p = paired_report("philosophy fail", philosophy_prog(), "🦍DungLang", philosophy_prog(), "🍠YakiimoIR")
    for r in [fed_s, fed_p]:
        mark = "✅" if r.trace_equal and r.kont_equal else "❌"
        print(f"  {mark} {r.case}: trace={r.trace_equal} kont={r.kont_equal} surface_diff={r.surface_diff}")

    banner("③ Temporal Banana Rewrite (GPT v2.1)")
    crisis = run_capture(civilization_crisis_prog(), frontend="🦍DungLang")
    store  = crisis.sink
    if crisis.error:
        print(f"  外交危機: {crisis.error.error_type}({crisis.error.error_message})")
    store.step_count = 88
    rewrites = store.temporal_banana_rewrite(10, max_rewrites=2)
    print(f"  {len(rewrites)}件の歴史を改変 / 公式歴史 {len(store.official_history)}件 / 考古学痕跡 {len(store.archaeology)}件")

    banner("④ Ghost Odor Archaeology (GPT v2.1)")
    ghost_v21, artifacts_v21 = mammoth_distributed_transaction()
    print(f"  {ghost_v21.detail}")
    for a in artifacts_v21: print(f"  {a.artifact_id}: confidence={a.confidence:.2f}")

    banner("⑤ Gorilla Incompleteness (GPT v2.1)")
    for stmt in ["おなら = 風", "おなら ≠ 風", "この定理は証明可能"]:
        r = GorillaTheoremProver.prove(stmt)
        print(f"  {r['statement']} → {r['result']}")

    banner("⑥ Causality Leak (GPT v2.1)")
    official_details = {ev.detail for ev in store.official_history}
    leaks = []
    for ev in store.archaeology:
        if ev.source_event not in official_details:
            leaks.append(CausalityLeakEvent(
                step=ev.step, kind="causality_leak",
                detail=f"公式歴史にない痕跡: {ev.source_event}",
                frontend="ArchaeologyIR", era="archaeological",
                leaked_from=ev.source_event, leaked_into=ev.artifact_id))
    print(f"  {len(leaks)}件の因果リーク: " + ", ".join(l.leaked_into for l in leaks))

    # ─ Claude v2.2 追加モジュール ─
    banner("⑦ OdorTypeInference — 臭気型推論器 (Claude v2.2)")
    type_cases = [
        ("純粋プログラム", (Assign("x", int_to_expr(3)), Flush(Var("x")))),
        ("外交危機プログラム", civilization_crisis_prog()),
        ("哲学型エラー", (Assign("q", PhilosophyExpr("存在とは何か")), Flush(Var("q")))),
        ("哲学型＋外交（複合汚染）",
         (Assign("q",  PhilosophyExpr("おならとは何か")),
          Assign("lv", int_to_expr(7)),
          DiplomaticFlush(OdorAdd(Var("q"), Var("lv")), "ウホ族", "バナナ族"))),
    ]
    type_results = []
    for name, prog in type_cases:
        result = infer_program(prog)
        mark = "✅" if result.ok() else "❌"
        print(f"\n  {mark} [{name}]")
        print(result.summary())
        type_results.append({"name": name, "ok": result.ok(),
                              "bindings": {k: v.name for k, v in result.env.bindings.items()}})

    banner("⑧ TwoPhaseCommit — マンモス2相コミット (Claude v2.2)")
    cases_2pc = [
        ("両洞窟成功 → CommittedOdor",
         (OdorFlush(OdorLevelExpr(5), source="マンモス"),),
         (Assign("x", int_to_expr(3)), Flush(Var("x")))),
        ("CaveA成功・CaveB失敗 → Ghost Odor",
         (OdorFlush(OdorLevelExpr(7), source="マンモス"),),
         (Flush(Var("missing_observer")),)),
        ("両洞窟失敗 → Clean Rollback",
         (Flush(Var("ghost_a")),),
         (Flush(Var("ghost_b")),)),
    ]
    all_2pc = []
    for label, pa, pb in cases_2pc:
        print(f"\n  [{label}]")
        r2pc = mammoth_2pc(pa, pb)
        print(f"  最終: {r2pc.final_status.value}")
        all_2pc.append(r2pc)

    banner("⑨ WitnessCouncil — 証人評議会 (Claude v2.2)")
    print(f"  {PHILOSOPHY_GORILLA_EXCUSE}\n")
    all_artifacts = list(store.archaeology) + artifacts_v21
    ghost_r = all_2pc[1]
    if ghost_r.artifacts: all_artifacts.extend(ghost_r.artifacts)
    council = council_review_all(all_artifacts)
    verdict_count = {v: 0 for v in ArtifactVerdict}
    for cr in council:
        verdict_count[cr.verdict] += 1
        icon = {"VERIFIED": "✅", "DISPUTED": "⚠️", "SEALED": "🔒"}[cr.verdict.value]
        print(f"  {icon} {cr.artifact_id}")
        print(f"     信頼度 {cr.original_confidence:.2f} → {cr.adjusted_confidence:.2f}  [{cr.verdict.value}]")
        print(f"     {cr.council_note}")
        for v in cr.votes:
            if v.vote == "除外": print(f"       {v.witness}: {v.reason}")
            else: print(f"       {v.witness} ({v.weight}x): {v.vote} — {v.reason}")
    print(f"\n  評議会集計: VERIFIED={verdict_count[ArtifactVerdict.VERIFIED]} "
          f"DISPUTED={verdict_count[ArtifactVerdict.DISPUTED]} "
          f"SEALED={verdict_count[ArtifactVerdict.SEALED]}")

    banner("★ Replay Civilization v2.2 🦍📜🔥")
    all_events = list(store.full_log) + [ghost_v21] + artifacts_v21 + leaks
    if ghost_r.ghost_event: all_events.append(ghost_r.ghost_event)
    if ghost_r.artifacts:   all_events.extend(ghost_r.artifacts)
    replay(all_events)

    report = {
        "version": "DungLang Civilization v2.2",
        "optimizer": opt_report.to_dict(),
        "federation": [fed_s.to_dict(), fed_p.to_dict()],
        "temporal_rewrites": [ev.to_dict() for ev in rewrites],
        "civilization_diff": civilization_diff(store),
        "ghost_odor_v21": ghost_v21.to_dict(),
        "two_phase_commit": [r.to_dict() for r in all_2pc],
        "type_inference": type_results,
        "witness_council": [cr.to_dict() for cr in council],
        "verdict_summary": {v.value: c for v, c in verdict_count.items()},
    }
    import os as _os
    _candidates = [
        "/mnt/user-data/outputs",   # Claude環境
        "/mnt/data",                # GPT環境
        "/tmp",                     # フォールバック
    ]
    _outdir = next((d for d in _candidates if _os.path.isdir(d)), "/tmp")
    out = _os.path.join(_outdir, "dunglang_civilization_v2_2_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    banner("v2.2 complete 🪨🔥📜")
    print(f"  JSON: {out}")
    print("""
  ① OdorOptimizer       (GPT)    ✅   ⑦ OdorTypeInference  (Claude) ✅
  ② Federation          (GPT)    ✅   ⑧ TwoPhaseCommit      (Claude) ✅
  ③ Temporal Rewrite    (GPT)    ✅   ⑨ WitnessCouncil      (Claude) ✅
  ④ Ghost Odor Arch.    (GPT)    ✅
  ⑤ Gorilla Incomplete  (GPT)    ✅
  ⑥ Causality Leak      (GPT)    ✅

  成功は同じ。失敗も同じ。型も同じ。証人だけが違うウホ。🪨🔥📜
""")


if __name__ == "__main__":
    main()
