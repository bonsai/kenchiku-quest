# kenchiku-quest

2級建築士試験4科目をゲーム化したブラウザ学習アプリ。

- 🏗️ **構造** — 物理シミュレーション（はり・トラス・S図M図・アーチ・吊り橋）
- 🌡️ **環境** — パラメータ調整（温熱・採光・換気・音・給排水）
- 🏗️ **施工** — 工程管理シミュ（ガント・リスク・安全・品質）
- 📋 **法規** — ケース判定クイズ（敷地・構造・設備・確認申請）

## URL

https://bonsai.github.io/kenchiku-quest/

## 技術

HTML5 + CSS3 + Vanilla JS。GitHub Pagesでホスティング。

## 開発

```
docs/
├── index.html              # ワールドマップ・タイトル
├── shared/                 # 共通エンジン
│   ├── css/kihon.css       # 共通スタイル
│   ├── js/engine.js        # セーブ/ロード・演出
│   └── js/quiz-engine.js   # クイズシステム
├── data/                   # オントロジー・過去問
│   ├── common-ontology.json
│   ├── structure-ontology.json
│   ├── environment-ontology.json
│   ├── construction-ontology.json
│   ├── regulation-ontology.json
│   └── exam-questions/     # 過去問4科目
├── structure/              # 構造ワールド
├── environment/            # 環境ワールド
├── construction/           # 施工ワールド
├── regulation/             # 法規ワールド
└── boss/                   # 最終ボス・統合試験
```
