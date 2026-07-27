# 器具設計書 2026-07-27

## 統合アーキテクチ　アールチーム構成

| 技術 | 言語 | 対象 | 成果物| 連携方法|
|-----|------|------|-------|---|
|Web API| Python3 | 環境計算・製図 | FastAPI Docker | HTTP JSON → 全フロント |
|ブラウザゲーム| TypeScript | 環境フロント・法規クイズ | React SPA + Canvas | HTTP → FastAPI |
|マイクラMod | Java 17 | 構造崩壊・力学シミュ | Fabric Mod JAR | 独立（ローカル計算） |
|マイクラ連携 | TypeScript | 法規敷地可視化 | mcfunction + Datapack | ファイルIO |
|製図エンジン | Python (bpy/ezdxf) | DWG/DXF出力 | CLIコマンド | FastAPIが subprocess起動 |
|Unity(VR)| C# | 未着手 | オプション | 後ろに |

## リポジトリ構造

```
bonsai/kenchiku-quest/              ← 主repo
├── docker-compose.yml              ← PostgreSQL + FastAPI + Nginx
├── py/                             ← Pythonエコシステム
│   ├── api/                        ← FastAPI本体
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── env.py             ← 環境シミュAPI
│   │   │   ├── structure.py       ← 構造計算API（Java Modからも呼ぶ）
│   │   │   ├── regu.py            ← 法規推論API
│   │   │   └── draw.py            ← 製図発注API
│   │   └── static/out/            ← 生成図面・3Dモデル
│   ├── sim/                        ← 数値シミュ本体
│   │   ├── heat.py                ← 熱計算
│   │   ├── light.py               ← 採光
│   │   └── wind.py                ← 風圧
│   ├── draw/                       ← 製図エンジン
│   │   ├── dxf_out.py             ← ezdxfラッパー
│   │   ├── bpy_regu.py            ← Blender法規3D
│   │   └── mpl_structure.py       ← matplotlib S図M図
│   └── ai/                         ← 未着手
│       └── claude_mcp.py          ← オプションでMCP連携
│
├── mc/                              ← Minecraftエコシステム（Java/TS）
│   ├── fabric-mod/                 ← Java Fabric Mod
│   │   ├── src/main/java/kenchiku/
│   │   │   ├── structure/BeamSimulator.java
│   │   │   ├── structure/StressBlockRenderer.java
│   │   │   └── common/KenchikuAPI.java  ← HTTP→FastAPI通信
│   │   └── build.gradle
│   └── datapack/                   ← TSで生成または手書きJSON
│       ├── kenchiku-quest/
│       │   ├── data/kenchiku/functions/
│       │   └── pack.mcmeta
│       └── scripts/gen-datapack.ts  ← Nodeで JSON批量生成
│
├── web/                             ← TypeScriptブラウザフロント
│   ├── src/
│   │   ├── env/                    ← 環境シミュ画面
│   │   ├── regu/                   ← 法規敷地エディタ
│   │   ├── boss/                   ← 総合試験
│   │   └── shared/                 ← APIクライアント
│   ├── package.json
│   └── vite.config.ts
│
├── rb/                              ← Roblox（オプション・TS）
│   └── src/
│       ├── construction/           ← 施工ゲーム
│       └── shared/
│
├── docs/                            ← GitHub Pages（ランディング）
│   └── index.html                  ← プロジェクト紹介・右下リンク集
│
└── design/
    ├── GAME-DESIGN-4SUBJECTS.md
    └── ISSUES.md                   ← これをmaster管理にする
```

## FastAPIエンドポイント設計

```
GET  /health                        ← ヘルスチェック
POST /api/v1/structure/beam         ← 梁計算 {b,h,P,L,E,fb}→σ,δ,ratio,broken
POST /api/v1/structure/cpm          ← CPM {tasks[]}→critical_path
GET  /api/v1/env/params             ← 環境計算パラメータ取得
POST /api/v1/env/simulate           ← 熱・光・音シミュ一括
POST /api/v1/regu/check             ← 法規判定 {site,bldg}→violations[]
POST /api/v1/draw/dxf               ← DXF発注 {plan_type,params}→file_url
POST /api/v1/draw/bpy               ← Blender発注 {type,scene}→glb_url
GET  /api/v1/quiz/{subject}         ← 過去問取得（ランダム）
POST /api/v1/game/save              ← プレイヤーセーブ
GET  /api/v1/game/load/{user_id}    ← プレイヤーロード
```

## マイクラMod ↔ Python連携設計

```java
// Java (Fabric) から HTTPでFastAPIを呼ぶ
KenchikuAPI.calculateBeam(b=180,h=200,P=20000)
  → 非同期HTTP POST → Python FastAPI 
  → JSONレスポンス → Java側でσを受取
  → ブロック破壊閾値として反映
```

```typescript
// TypeScript (Datapack生成) からはCLIでPythonを叩く
// gen-datapack.ts
import { execSync } from 'child_process';
const result = execSync('python3 py/regu/check.py --site input.json');
const violations = JSON.parse(result);
// violations → mcfunctionコマンド生成
```

## Docker Compose（開発環境）

```yaml
services:
  api:
    build: ./py/api
    ports: ["8000:8000"]
    volumes: ["./py:/app", "./data:/data"]
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: kenchiku
  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes: ["./web/dist:/usr/share/nginx/html", "./py/api/static:/static"]
```

## ビルド・デプロイフロー

```
開発者PC
├── py/api/      → docker build → クラウド（CloudRun or Azure Container）
├── web/         → npm run build → dist/ → nginx or Vercel
├── mc/fabric/   → ./gradlew build → JAR → CurseForge or 自鯖
└── mc/datapack/ → npm run gen  → zip → 配布
```

## 次アクション（優先順）

1. **[NOW]** `docker-compose.yml` + `Dockerfile` 作成 → ローカル統合環境構築
2. **[NOW]** `py/api/routers/` を `main.py` から分割リファクタ
3. **[+1h]** `web/` Viteプロジェクト初期化
4. **[+2h]** `mc/fabric/` Gradleプロジェクト初期化
5. **[+3h]** `mc/datapack/scripts/gen-datapack.ts` 作成

全部並行でやる。