import sqlite3
import os
import subprocess
import tempfile

DB_PATH = "Database/morphic_autonomy.db"

def compile_all_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # source_c が存在する全プリミティブを取得
    cursor.execute("SELECT id, source_c FROM primitives WHERE source_c IS NOT NULL")
    rows = cursor.fetchall()
    
    for pid, source in rows:
        print(f"[*] Compiling Wasm for primitive: {pid}...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            c_path = os.path.join(tmpdir, "input.c")
            wasm_path = os.path.join(tmpdir, "output.wasm")
            
            with open(c_path, "w") as f:
                f.write(source)
            
            try:
                # emcc コマンドで Wasm (Side Module) へコンパイル
                # -O3: 最適化
                # -s WASM=1: Wasm出力
                # -s SIDE_MODULE=1: メイン関数なしのモジュール
                # --no-entry: エントリポイントなし
                subprocess.run([
                    "emcc", c_path, 
                    "-O3",
                    "-s", "WASM=1", 
                    "-s", "SIDE_MODULE=1",
                    "--no-entry",
                    "-o", wasm_path
                ], check=True, capture_output=True)
                
                with open(wasm_path, "rb") as f:
                    wasm_binary = f.read()
                    
                cursor.execute("UPDATE primitives SET binary_wasm = ? WHERE id = ?", (wasm_binary, pid))
                print(f"[SUCCESS] {pid}.wasm generated and stored in MQDB. ({len(wasm_binary)} bytes)")
                
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to compile {pid}:")
                print(e.stderr.decode())
            except Exception as e:
                print(f"[ERROR] Unexpected error for {pid}: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    compile_all_from_db()
