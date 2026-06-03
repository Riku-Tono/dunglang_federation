# -*- coding: utf-8 -*-
"""
DungLang Civilization v3.0
===========================
v2.2 に ⑩〜⑬ を追加した文明発生シミュレータ完全体ウホ。

追加:
  ⑩ Constitution Federation  — 憲法・条文・違反イベント
  ⑪ Election System          — 評議会選挙・政権で判決が変わる
  ⑫ Civilization Metrics     — 安定度・外交緊張・哲学汚染・歴史改変率
  ⑬ Myth Generator           — 消された歴史が伝説・神話へ変換される

合言葉:
  成功は同じ。失敗も同じ。歴史が消えても、神話が残るウホ。
"""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


@dataclass(frozen=True)
class CivEvent:
    step: int
    kind: str
    detail: str
    frontend: str = "🦍DungLang"
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
class GhostOdorEvent(CivEvent):
    cave_a: str = "🦣CaveA"
    cave_b: str = "🦣CaveB"
    odor_level: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"cave_a": self.cave_a, "cave_b": self.cave_b, "odor_level": self.odor_level})
        return d


@dataclass(frozen=True)
class HistoryRewriteEvent(CivEvent):
    erased_event: str = ""
    rewritten_as: str = "最初から存在しなかったことになった"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"erased_event": self.erased_event, "rewritten_as": self.rewritten_as})
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
            "confidence": round(self.confidence, 3),
        })
        return d


@dataclass(frozen=True)
class ConstitutionArticle:
    article_no: int
    title: str
    rule: str

    def to_dict(self) -> dict:
        return {"article_no": self.article_no, "title": self.title, "rule": self.rule}


@dataclass(frozen=True)
class ConstitutionViolationEvent(CivEvent):
    article_no: int = 0
    article_title: str = ""
    offender: str = ""
    severity: int = 1

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "article_no": self.article_no,
            "article_title": self.article_title,
            "offender": self.offender,
            "severity": self.severity,
        })
        return d


class ConstitutionFederation:
    def __init__(self) -> None:
        self.articles = [
            ConstitutionArticle(1, "証人資格", "哲学ゴリラは証人になれない"),
            ConstitutionArticle(2, "GhostOdor無罪推定", "GhostOdorは直接有罪推定しない"),
            ConstitutionArticle(3, "バナナ歴史改変権", "バナナ3本以上で歴史改変を申請できる"),
            ConstitutionArticle(4, "越境臭気外交", "GhostOdorの越境発生は外交案件である"),
        ]

    def check(self, action: str, *, actor: str, step: int) -> Optional[ConstitutionViolationEvent]:
        if action == "philosophy_gorilla_witness" and "哲学ゴリラ" in actor:
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ 第1条違反: 哲学ゴリラを証人にした",
                "ConstitutionIR", "legal", 1, "証人資格", actor, 5
            )
        if action == "convict_ghost_odor":
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ 第2条違反: GhostOdorを直接有罪にした",
                "ConstitutionIR", "legal", 2, "GhostOdor無罪推定", actor, 4
            )
        if action == "banana_rewrite" and actor == "バナナ2本":
            return ConstitutionViolationEvent(
                step, "constitution_violation", "⚖️ 第3条違反: バナナ不足で歴史改変を試みた",
                "ConstitutionIR", "legal", 3, "バナナ歴史改変権", actor, 3
            )
        return None

    def to_dict(self) -> dict:
        return {"articles": [a.to_dict() for a in self.articles]}


class Policy(Enum):
    STRICT = auto()
    BALANCED = auto()
    BANANA_POPULIST = auto()
    REVOLUTIONARY = auto()

    def pretty(self) -> str:
        return {
            Policy.STRICT: "厳罰主義",
            Policy.BALANCED: "中庸評議",
            Policy.BANANA_POPULIST: "バナナ福祉主義",
            Policy.REVOLUTIONARY: "革命的無罪主義",
        }[self]


@dataclass(frozen=True)
class Candidate:
    name: str
    party: str
    policy: Policy


@dataclass(frozen=True)
class ElectionResult:
    step: int
    term_no: int
    winners: list[Candidate]
    vote_share: dict[str, float]

    def to_event(self) -> CivEvent:
        winners = ", ".join(c.name for c in self.winners)
        return CivEvent(
            self.step, "election",
            f"🗳️ CouncilTerm #{self.term_no}: {winners} が当選",
            "ElectionIR", "political"
        )

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "term_no": self.term_no,
            "winners": [{"name": c.name, "party": c.party, "policy": c.policy.pretty()} for c in self.winners],
            "vote_share": self.vote_share,
        }


class ElectionSystem:
    def __init__(self, seed: int = 30) -> None:
        self.rng = random.Random(seed)
        self.candidates = [
            Candidate("研究ゴリラ", "実証党", Policy.BALANCED),
            Candidate("気象ゴリラ", "風向党", Policy.BALANCED),
            Candidate("法務ゴリラ", "石板法治党", Policy.STRICT),
            Candidate("バナナ党ゴリラ", "バナナ党", Policy.BANANA_POPULIST),
            Candidate("革命ゴリラ", "洞窟革命戦線", Policy.REVOLUTIONARY),
        ]

    def run_election(self, *, step: int, term_no: int) -> ElectionResult:
        raw = {c.name: self.rng.uniform(0.05, 0.35) for c in self.candidates}
        total = sum(raw.values())
        shares = {k: round(v / total, 3) for k, v in raw.items()}
        winners = sorted(self.candidates, key=lambda c: shares[c.name], reverse=True)[:3]
        return ElectionResult(step, term_no, winners, shares)

    @staticmethod
    def verdict_for_ghost_odor(result: ElectionResult) -> str:
        policies = [c.policy for c in result.winners]
        if Policy.REVOLUTIONARY in policies:
            return "GhostOdor → 無罪。臭気は民衆の自己表現ウホ"
        if Policy.STRICT in policies:
            return "GhostOdor → 要調査。石板監査を継続ウホ"
        if Policy.BANANA_POPULIST in policies:
            return "GhostOdor → バナナ配布で鎮静化ウホ"
        return "GhostOdor → 保留。気象ゴリラの証言待ちウホ"


@dataclass(frozen=True)
class CivilizationMetrics:
    stability: float
    diplomatic_tension: float
    philosophy_pollution: float
    history_rewrite_rate: float
    ghost_odor_count: int
    myth_pressure: float

    def to_dict(self) -> dict:
        return {
            "stability": round(self.stability, 3),
            "diplomatic_tension": round(self.diplomatic_tension, 3),
            "philosophy_pollution": round(self.philosophy_pollution, 3),
            "history_rewrite_rate": round(self.history_rewrite_rate, 3),
            "ghost_odor_count": self.ghost_odor_count,
            "myth_pressure": round(self.myth_pressure, 3),
        }

    def dashboard(self) -> str:
        def bar(x: float) -> str:
            n = max(0, min(10, int(round(x / 10))))
            return "█" * n + "░" * (10 - n) + f" {x:5.1f}%"
        return "\n".join([
            "📊 Civilization Metrics",
            f"  文明安定度       {bar(self.stability)}",
            f"  外交緊張度       {bar(self.diplomatic_tension)}",
            f"  哲学汚染度       {bar(self.philosophy_pollution)}",
            f"  歴史改変率       {bar(self.history_rewrite_rate)}",
            f"  神話圧           {bar(self.myth_pressure)}",
            f"  GhostOdor残存数  {self.ghost_odor_count}",
        ])


class MetricsEngine:
    @staticmethod
    def compute(events: list[CivEvent]) -> CivilizationMetrics:
        total = max(1, len(events))
        diplomatic = sum(1 for e in events if e.kind == "diplomatic")
        violations = sum(1 for e in events if e.kind == "constitution_violation")
        rewrites = sum(1 for e in events if e.kind == "history_rewrite")
        ghosts = sum(1 for e in events if e.kind == "ghost_odor")
        myths = sum(1 for e in events if e.kind in {"legend", "myth", "religion"})
        philosophy = sum(1 for e in events if "哲学" in e.detail)

        diplomatic_tension = min(100.0, diplomatic * 18 + violations * 12 + ghosts * 8)
        philosophy_pollution = min(100.0, philosophy * 24 + violations * 6)
        history_rewrite_rate = min(100.0, rewrites / total * 100)
        myth_pressure = min(100.0, myths * 22 + ghosts * 10 + rewrites * 8)
        stability = max(0.0, 100.0 - diplomatic_tension * 0.35 - philosophy_pollution * 0.25 - history_rewrite_rate * 0.4)
        return CivilizationMetrics(stability, diplomatic_tension, philosophy_pollution, history_rewrite_rate, ghosts, myth_pressure)


@dataclass(frozen=True)
class LegendEvent(CivEvent):
    source_events: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"source_events": list(self.source_events)})
        return d


@dataclass(frozen=True)
class MythEvent(CivEvent):
    myth_id: str = ""
    doctrine: str = ""
    source_events: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "myth_id": self.myth_id,
            "doctrine": self.doctrine,
            "source_events": list(self.source_events),
        })
        return d


class MythGenerator:
    @staticmethod
    def generate(official: list[CivEvent], archaeology: list[ArchaeologicalArtifact], ghosts: list[GhostOdorEvent], *, step: int) -> tuple[LegendEvent, MythEvent, CivEvent]:
        official_details = {e.detail for e in official}
        hidden = [a for a in archaeology if a.source_event not in official_details]
        source_lines = tuple(a.source_event for a in hidden[:4]) + tuple(g.detail for g in ghosts[:2])

        legend_text = (
            "📜 伝説: かつて見えざる臭気が洞窟から洞窟へ渡った。"
            "誰も責任を取らず、石板だけが震えた。"
        )
        myth_text = (
            "✨ 神話: 三本のバナナが捧げられた時、事件は歴史から消えた。"
            "だが壁画は沈黙せず、GhostOdorは夜の風として戻る。"
        )
        doctrine = "臭気は消えない。記録だけが消える。"

        legend = LegendEvent(step, "legend", legend_text, "MythIR", "legendary", source_lines)
        myth = MythEvent(step + 450, "myth", myth_text, "MythIR", "mythic", "MYTH-GHOST-ODOR-001", doctrine, source_lines)
        religion = CivEvent(step + 600, "religion", "⛪ GhostOdor教成立: 教義『臭気は消えない、記録だけが消える』", "MythIR", "religious")
        return legend, myth, religion


@dataclass
class CivilizationStore:
    events: list[CivEvent] = field(default_factory=list)
    official_history: list[CivEvent] = field(default_factory=list)
    archaeology: list[ArchaeologicalArtifact] = field(default_factory=list)

    def emit(self, ev: CivEvent, *, official: bool = True) -> None:
        self.events.append(ev)
        if official:
            self.official_history.append(ev)

    def temporal_banana_rewrite(self, *, step: int, banana_count: int, max_rewrites: int = 2) -> list[HistoryRewriteEvent]:
        if banana_count < 3:
            self.emit(CivEvent(step, "banana_failed", f"🍌×{banana_count}: 歴史改変失敗", "BananaGC", "meta"), official=False)
            return []

        victims = list(self.official_history[:max_rewrites])
        rewrites: list[HistoryRewriteEvent] = []
        for idx, old in enumerate(victims, 1):
            rewrite = HistoryRewriteEvent(
                step, "history_rewrite", f"🍌×{banana_count}: 公式歴史を改変",
                "BananaGC", "meta", old.detail
            )
            artifact = ArchaeologicalArtifact(
                step, "artifact", f"🪨 壁画痕跡: {old.detail}",
                "ArchaeologyIR", "archaeological", f"ART-{step}-{idx}", old.detail, 0.35 + banana_count / 20
            )
            self.events.extend([rewrite, artifact])
            self.archaeology.append(artifact)
            rewrites.append(rewrite)

        self.official_history = [e for e in self.official_history if e not in victims]
        self.emit(CivEvent(step, "banana_gc", f"🍌×{banana_count}: {len(victims)}件が公式歴史から消滅", "BananaGC", "meta"), official=False)
        return rewrites

    def replay(self) -> str:
        lines = ["📜 Replay Civilization v3.0"]
        for ev in sorted(self.events, key=lambda e: (e.step, e.kind, e.detail)):
            icon = {
                "odor": "💨", "diplomatic": "🌍", "ghost_odor": "👻",
                "history_rewrite": "📜🔥", "artifact": "🪨",
                "constitution": "⚖️", "constitution_violation": "🚨",
                "election": "🗳️", "legend": "📜", "myth": "✨",
                "religion": "⛪", "banana_gc": "🍌", "council_verdict": "🏛️",
            }.get(ev.kind, "・")
            lines.append(f"  step {ev.step:>4} | {icon} [{ev.era}] {ev.detail}")
        return "\n".join(lines)


def banner(title: str) -> None:
    print("\n" + "━" * 76)
    print(f"  {title}")
    print("━" * 76)


def build_civilization() -> tuple[CivilizationStore, dict]:
    store = CivilizationStore()
    constitution = ConstitutionFederation()

    store.emit(CivEvent(6, "odor", "💨 Lv7(マンモス)", "🦍DungLang"))
    store.emit(CivEvent(42, "diplomatic", "🌍 ウホ族→バナナ族 濃度7 バナナ14本", "🦍DungLang"))

    ghost = GhostOdorEvent(
        55, "ghost_odor", "👻 Ghost Odor Lv5: CaveAコミット済み・CaveBロールバック",
        "2PCIR", "liminal", "🦣CaveA", "🦣CaveB", 5
    )
    store.emit(ghost, official=False)

    store.emit(CivEvent(120, "constitution", "⚖️ DungLang憲法制定: GhostOdor無罪推定を採択", "ConstitutionIR", "legal"))

    for action, actor, step in [
        ("convict_ghost_odor", "法務ゴリラ", 150),
        ("philosophy_gorilla_witness", "哲学ゴリラ", 151),
    ]:
        violation = constitution.check(action, actor=actor, step=step)
        if violation:
            store.emit(violation, official=False)

    election_system = ElectionSystem(seed=300)
    election = election_system.run_election(step=200, term_no=17)
    store.emit(election.to_event())
    ghost_verdict = election_system.verdict_for_ghost_odor(election)
    store.emit(CivEvent(210, "council_verdict", f"評議会判決: {ghost_verdict}", "CouncilIR", "political"))

    rewrites = store.temporal_banana_rewrite(step=300, banana_count=3, max_rewrites=2)

    legend, myth, religion = MythGenerator.generate(store.official_history, store.archaeology, [ghost], step=450)
    store.emit(legend, official=False)
    store.emit(myth, official=False)
    store.emit(religion, official=False)

    metrics = MetricsEngine.compute(store.events)

    report = {
        "version": "DungLang Civilization v3.0",
        "constitution": constitution.to_dict(),
        "election": election.to_dict(),
        "ghost_verdict": ghost_verdict,
        "history_rewrites": [r.to_dict() for r in rewrites],
        "metrics": metrics.to_dict(),
        "events": [e.to_dict() for e in store.events],
        "official_history": [e.to_dict() for e in store.official_history],
        "archaeology": [a.to_dict() for a in store.archaeology],
    }
    return store, report


def main() -> None:
    banner("DungLang Civilization v3.0 🦍🔥🪨⚖️🗳️📜✨")
    print("  v2.2 + ⑩ Constitution Federation + ⑪ Election System + ⑫ Metrics + ⑬ Myth Generator")

    store, report = build_civilization()
    metrics = CivilizationMetrics(**report["metrics"])

    banner("⑩ Constitution Federation")
    for article in report["constitution"]["articles"]:
        print(f"  第{article['article_no']}条 {article['title']}: {article['rule']}")

    banner("⑪ Election System")
    print(f"  CouncilTerm #{report['election']['term_no']}")
    for name, share in sorted(report["election"]["vote_share"].items(), key=lambda kv: kv[1], reverse=True):
        print(f"    {name:<10} {share * 100:5.1f}%")
    print(f"  判決: {report['ghost_verdict']}")

    banner("⑫ Civilization Metrics")
    print(metrics.dashboard())

    banner("⑬ Myth Generator")
    myths = [e for e in store.events if e.kind in {"legend", "myth", "religion"}]
    for ev in myths:
        print(f"  step {ev.step}: {ev.detail}")

    banner("Replay Civilization")
    print(store.replay())

    outdir = "/mnt/data" if os.path.isdir("/mnt/data") else "."
    out = os.path.join(outdir, "dunglang_civilization_v3_0_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    banner("v3.0 complete")
    print(f"  JSON report: {out}")
    print("  成功は同じ。失敗も同じ。歴史が消えても、神話が残るウホ。")


if __name__ == "__main__":
    main()
