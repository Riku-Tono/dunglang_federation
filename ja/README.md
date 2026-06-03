# DungLang Federation 4.0

> **プロトタイプ / デモ / ショーケース** — 完全なコンパイラや形式的証明ではありません。

DungLang Federation 4.0 は、DungLang Federation プロトタイプ系列を統合したショーケース版です。  
Federation 1.0 の中核である「橋渡し」のアイデアに、Civilization v2 / v2.1 / v3.0 のシミュレーション層を組み合わせています。  
含まれる要素は、イベント履歴、履歴の書き換え、憲法、選挙、文明メトリクス、神話生成です。

古いバージョンは開発履歴として `/versions` に保存されています。

---

## アーキテクチャ

```
Frontends
DungLang / ScatLang / SeaIR / YakiimoIR
        ↓
Odor IR（共有中間表現）
OdorZeroExpr / OdorSuccExpr / Var / OdorAdd / ...
        ↓
CEK Cave Machine
State(Control, Env, Kont) → OdorSink
        ↓
Civilization Stack
CivilizationStore → ConstitutionFederation
ElectionSystem → MythGenerator → CivilizationMetrics
        ↓
outputs/dunglang_federation_4_0_report.json
```

---

## モジュール

| Module | From | Description |
|---|---|---|
| Odor IR + CEK Cave Machine | Federation 1.0 | 複数のフロントエンドを共有 IR にコンパイルし、CEK 風のマシンで実行する |
| OdorSink / DiplomaticEvent | Federation 1.0 | 匂いの観測、部族間の外交イベント、banana GC |
| Error Federation | Federation 1.0 | 代表ケースの確認: 同じ IR → フロントエンド間で同じエラー形状 |
| OdorOptimizer | Civilization v2.0 | 匂いレベルに対する定数畳み込みパス |
| Ghost Odor / BananaRewrite | Civilization v2.1 | 2PC ghost odor イベント、banana token による時間的履歴書き換え |
| OdorTypeInference / WitnessCouncil | Civilization v2.2 | 静的な匂い型推論デモ、哲学者ゴリラ除外つき artifact witness council |
| Constitution Federation | Civilization v3.0 | 4つの憲法条文、違反時に violation event を発行 |
| Election System | Civilization v3.0 | 政策派閥を持つ評議会選挙、Ghost Odor に対する判定が支配連合によって変わる |
| CivilizationMetrics | Civilization v3.0 | 安定性、外交的緊張、哲学汚染、神話圧力のダッシュボード |
| MythGenerator | Civilization v3.0 | 消された公式履歴 → 伝説 → 神話 → 宗教、というパイプライン |

---

## バージョン履歴

| Version | Highlight |
|---|---|
| Federation 1.0 | Odor IR bridge、CEK Cave Machine、Error Federation の代表ケース |
| Civilization v2.0 | OdorOptimizer、Kont Federation、History Federation |
| Civilization v2.1 | Temporal Banana Rewrite、Ghost Odor Archaeology、Causality Leak Detector |
| Civilization v2.2 | OdorTypeInference、TwoPhaseCommit、WitnessCouncil |
| Civilization v3.0 | Constitution Federation、Election System、CivMetrics、MythGenerator |
| **Federation 4.0** | **すべての層を統合した公開ショーケース** |

古いバージョンは `/versions` に保存されています。

---

## 実行方法

```bash
python dunglang_federation_4_0.py
```

出力: `outputs/dunglang_federation_4_0_report.json`

レポートには、次の5つのトップレベルセクションが含まれます。

```
meta              バージョン情報、注意書き、履歴
cek_demos         4つすべてのフロントエンドに対する CEK machine 実行
odor_optimizer    代表的な匂いレベルに対する定数畳み込み結果
error_federation  対になったエラー形状チェック
civilization      憲法、選挙、書き換え、メトリクス、神話、リプレイを含む文明実行
```

---

## Replay Viewer

`dunglang_civilization_replay_viewer.html` は、文明イベントを見るためのブラウザベースの2ペイン式タイムラインビューアです。  
v2.1 向けに作られていますが、Federation 4.0 のイベント形状とも互換性があります。

**公式履歴** と **秘密ログ** を横並びで表示し、イベント種別ごとのフィルターボタンと、再生速度の設定を備えています。

このファイルはブラウザで直接開けます。サーバーは不要です。

---

## スコープと制限

このプロジェクトは **プロトタイプ / デモ / ショーケース** です。

- DungLang フロントエンドは、v0.7 のイベント構造を Odor IR に対応づけるものです。完全な DungLang パーサーではありません。
- Error Federation は代表ケースだけを確認します。異なる構文パーサー間の完全な形式的等価性証明ではありません。
- BananaGC はこのデモでは実行後の Sink 操作として動きます。ネイティブな CEK 命令ではありません。
- philosopher-gorilla 例外の比較は、同じ IR を2つのフロントエンド名の下で実行するものです。これは最小限の surface-diff チェックであり、クロスパーサー証明ではありません。

---

## モットー

> 表面の書き方は違う。地下の配管は同じ。 — ウホ
>
> 成功は同じ。失敗も同じ。歴史は消える。神話は残る。 — ウホ
```
