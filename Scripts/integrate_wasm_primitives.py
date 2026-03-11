import sqlite3
import os
import subprocess

DB_PATH = "Database/morphic_autonomy.db"

# 1. C言語でのプリミティブ設計図 (DNAの源)
C_PRIMITIVES = {
    "add": """
float builtin_add(float a, float b) {
    return a + b;
}
""",
    "distance_2d": """
#include <math.h>
float builtin_distance_2d(float x1, float y1, float x2, float y2) {
    return sqrtf(powf(x1 - x2, 2) + powf(y1 - y2, 2));
}
""",
    "sqrt": """
#include <math.h>
float builtin_sqrt(float a) {
    return sqrtf(a);
}
"""
}

def integrate_c_sources():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for pid, source in C_PRIMITIVES.items():
        print(f"[*] Integrating C Source for: {pid}")
        cursor.execute("UPDATE primitives SET source_c = ? WHERE id = ?", (source.strip(), pid))
    
    conn.commit()
    conn.close()

def compile_to_wasm_and_store(pid):
    """
    DB から C ソースを取得し、Wasm にコンパイルして DB に格納する
    (この環境に emcc 等があることを想定したパイプライン)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT source_c FROM primitives WHERE id = ?", (pid,))
    row = cursor.fetchone()
    if not row or not row[0]: return

    source_code = row[0]
    c_file = f"temp_{pid}.c"
    wasm_file = f"temp_{pid}.wasm"

    with open(c_file, "w") as f:
        f.write(source_code)

    # Wasm へのコンパイルコマンド (Emscripten または WASI-SDK)
    # ここでは概念実証のため、コンパイルが失敗しても DB 構造の維持を優先する
    try:
        # 実行例: emcc temp_add.c -s WASM=1 -s SIDE_MODULE=1 -o temp_add.wasm
        # 現在の環境でコンパイラがない場合はスキップ
        print(f"[*] Attempting Wasm compilation for: {pid}")
        # subprocess.run(["emcc", c_file, "-s", "WASM=1", "-o", wasm_file], check=True)
        
        # プレースホルダーとしてのバイナリ（実際にはコンパイル済みバイナリを読み込む）
        if os.path.exists(wasm_file):
            with open(wasm_file, "rb") as f:
                wasm_binary = f.read()
                cursor.execute("UPDATE primitives SET binary_wasm = ? WHERE id = ?", (wasm_binary, pid))
                print(f"[SUCCESS] Wasm stored for: {pid}")
    except Exception as e:
        print(f"[SKIP] Compilation skipped or failed: {e}")
    finally:
        if os.path.exists(c_file): os.remove(c_file)
        if os.path.exists(wasm_file): os.remove(wasm_file)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Integrating C sources into MQDB...")
    integrate_c_sources()
    
    # 統合されたソースの確認
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_c FROM primitives WHERE source_c IS NOT NULL")
    for row in cursor.fetchall():
        print(f"\n--- Primitive: {row[0]} ---")
        print(row[1])
    conn.close()
