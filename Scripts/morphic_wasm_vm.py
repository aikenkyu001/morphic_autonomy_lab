import sqlite3
import wasmtime
import struct
import json
import math

class MorphicWasmVM:
    def __init__(self, db_path="Database/morphic_autonomy.db"):
        self.db_path = db_path
        self.engine = wasmtime.Engine()
        self.store = wasmtime.Store(self.engine)
        self.wasm_cache = {}
        self.id_to_label = {}
        self._load_lexicon()
        
        # ホスト提供の基本関数 (Wasm がインポートを要求する場合のフォールバック)
        self.linker = wasmtime.Linker(self.engine)
        # 修正: linker.define_func は Store を取らない
        self.linker.define_func("env", "powf", wasmtime.FuncType([wasmtime.ValType.f32(), wasmtime.ValType.f32()], [wasmtime.ValType.f32()]), lambda a, b: math.pow(a, b))
        self.linker.define_func("env", "logf", wasmtime.FuncType([wasmtime.ValType.f32()], [wasmtime.ValType.f32()]), lambda a: math.log(a))
        self.linker.define_func("env", "expf", wasmtime.FuncType([wasmtime.ValType.f32()], [wasmtime.ValType.f32()]), lambda a: math.exp(a))
        self.linker.define_func("env", "sqrtf", wasmtime.FuncType([wasmtime.ValType.f32()], [wasmtime.ValType.f32()]), lambda a: math.sqrt(a))

    def _load_lexicon(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT integer_id, id FROM lexicon")
        for row in cursor.fetchall():
            self.id_to_label[row[0]] = row[1]
        conn.close()

    def get_wasm_instance(self, pid):
        if pid in self.wasm_cache:
            return self.wasm_cache[pid]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT binary_wasm FROM primitives WHERE id = ?", (pid,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            raise ValueError(f"Wasm binary not found for primitive: {pid}")

        module = wasmtime.Module(self.engine, row[0])
        instance = self.linker.instantiate(self.store, module)
        self.wasm_cache[pid] = instance
        return instance

    def execute_dna(self, dna, inputs):
        current_val = inputs
        for i in range(0, len(dna), 2):
            integer_id = struct.unpack("H", dna[i:i+2])[0]
            pid = self.id_to_label.get(integer_id)
            instance = self.get_wasm_instance(pid)
            func_name = f"builtin_{pid}"
            func = instance.exports(self.store)[func_name]
            
            if isinstance(current_val, list):
                if len(current_val) == 2:
                    current_val = func(self.store, float(current_val[0]), float(current_val[1]))
                else:
                    current_val = func(self.store, float(current_val[0]))
            else:
                current_val = func(self.store, float(current_val))
        return current_val

    def run_task(self, task_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.test_cases_json, w.quantum_dna 
            FROM tasks t 
            JOIN wisdom w ON t.id = w.id 
            WHERE t.id = ?
        """, (task_id,))
        row = cursor.fetchone()
        conn.close()
        if not row or not row[1]:
            print(f"[ERROR] No DNA found for task: {task_id}")
            return
        test_cases = json.loads(row[0])
        dna = row[1]
        print(f"[*] Running Task: {task_id} (Wasm Mode)")
        success = 0
        for tc in test_cases:
            res = self.execute_dna(dna, tc["input"])
            expected = tc["output"]
            if abs(res - expected) < 1e-4:
                success += 1
            else:
                print(f"  [FAIL] Input {tc['input']}: Expected {expected}, Got {res}")
        print(f"[*] Result: {success}/{len(test_cases)} Passed. {'[SUCCESS]' if success == len(test_cases) else '[FAILURE]'}")

if __name__ == "__main__":
    import sys
    vm = MorphicWasmVM()
    if len(sys.argv) > 1:
        vm.run_task(sys.argv[1])
    else:
        for tid in ["potential_energy", "geometric_mean", "log_of_power", "exp_of_sum"]:
            vm.run_task(tid)
