# Morphic Autonomy: 運用マニュアル (Operations Manual)

**著者:** Fumio Miyata

## 1. 知能の教育プロトコル (Education Protocol)
新しい能力をシステムに授けるための標準手順：
1.  **能力定義**: C 言語でプリミティブ（原子論理）を記述し、MQDB の `primitives` テーブルへ格納。
2.  **実体化**: `Scripts/compile_db_wasm.py` を実行し、Wasm バイナリを生成。
3.  **課題設定**: `Tasks/` に I/O 契約（JSON）を作成。
4.  **検証**: `Scripts/morphic_wasm_vm.py` で正解を確認。

## 2. 実験再現プロトコル (Reproduction Protocol)
追試者が 100% の精度で実験を再現するための手順：
- `Docs/REPRODUCTION_PROTOCOL.md` (詳細版) に基づき、環境構築（wasmtime, emscripten）を行う。
- MQDB を初期化し、自律学習とクロスカーネル実行を順次確認する。

## 3. 5秒探索プロトコル (Discovery Rule)
- 各課題の探索リミットは厳格に **5.0秒** とする。
- 時間内に解けない課題は `Unsolved/` へ自動隔離し、人間（Fumio Miyata）による直接教育の対象とする。

---
**© 2026 Fumio Miyata. All Rights Reserved.**
