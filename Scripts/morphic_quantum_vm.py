import sqlite3
import json
import struct
import math
from dataclasses import dataclass
from typing import Any

# 互換性のためのクラス定義
@dataclass(frozen=True)
class MorphicValue: pass

@dataclass(frozen=True)
class VLiteral(MorphicValue):
    value: Any

class MorphicQuantumVM:
    def __init__(self, db_path="Database/morphic_autonomy.db"):
        self.db_path = db_path
        self.primitives = {}
        self.id_to_label = {}
        self._load_from_db()

    def _load_from_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT integer_id, id FROM lexicon")
        for row in cursor.fetchall():
            self.id_to_label[row[0]] = row[1]
        
        cursor.execute("SELECT id, source_code FROM primitives WHERE impl_type = 'python'")
        for row in cursor.fetchall():
            pid, code = row
            indented_code = "\n".join(["    " + line for line in code.split("\n")])
            # 標準ライブラリを名前空間に提供
            import os, collections, heapq, json
            namespace = {
                "math": math, "os": os, "collections": collections, 
                "heapq": heapq, "json": json,
                "self": self, "VLiteral": VLiteral
            }
            try:
                exec(f"def func(self, args):\n{indented_code}", namespace)
                self.primitives[pid] = namespace["func"]
            except Exception as e:
                print(f"Error loading primitive {pid}: {e}")
        conn.close()

    def execute_dna(self, dna, raw_inputs):
        if not dna:
            return None
        
        # 入力を VLiteral でラップする
        current_args = [VLiteral(v) for v in raw_inputs]
        
        for i in range(0, len(dna), 2):
            integer_id = struct.unpack("H", dna[i:i+2])[0]
            label = self.id_to_label.get(integer_id)
            
            if label in self.primitives:
                # 実行
                res = self.primitives[label](self, current_args)
                # 結果を次の入力用にラップ (単一の結果が返ることを想定)
                if isinstance(res, VLiteral):
                    current_args = [res]
                else:
                    current_args = [VLiteral(res)]
            else:
                raise ValueError(f"Primitive ID {integer_id} ({label}) not found in VM.")
        
        # 最終結果をアンラップして返す
        final_res = current_args[0]
        return final_res.value if isinstance(final_res, VLiteral) else final_res

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
        if not row or not row[1]:
            return False

        test_cases = json.loads(row[0])
        dna = row[1]
        
        print(f"Running Task: {task_id} using Morphic DNA...")
        success_count = 0
        for i, tc in enumerate(test_cases):
            inp = tc["input"]
            expected = tc["output"]
            try:
                args = inp if isinstance(inp, list) else [inp]
                result = self.execute_dna(dna, args)
                if result == expected:
                    success_count += 1
                else:
                    print(f"  Test Case {i} FAILED: Expected {expected}, got {result}")
            except Exception as e:
                print(f"  Test Case {i} ERROR: {e}")

        is_perfect = success_count == len(test_cases)
        print(f"Result: {success_count}/{len(test_cases)} Passed. {'[SUCCESS]' if is_perfect else '[FAILURE]'}")
        return is_perfect

if __name__ == "__main__":
    vm = MorphicQuantumVM()
    test_tasks = ["hypotenuse_task", "matrix_product_determinant", "distance_formula", "quadratic_discriminant"]
    for tid in test_tasks:
        vm.run_task(tid)
