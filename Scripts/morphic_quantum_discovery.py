import sqlite3
import json
import struct
import signal
import time
import sys
from morphic_wasm_vm import MorphicWasmVM

class MorphicQuantumDiscovery:
    def __init__(self, db_path="Database/morphic_autonomy.db"):
        self.db_path = db_path
        self.vm = MorphicWasmVM(db_path)
        self.primitives = list(self.vm.id_to_label.values())
        self.pid_to_int = {}
        self._load_lexicon()

    def _load_lexicon(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, integer_id FROM lexicon")
        for row in cursor.fetchall():
            self.pid_to_int[row[0]] = row[1]
        conn.close()

    def _timeout_handler(self, signum, frame):
        raise TimeoutError("Discovery reached 5s limit.")

    def discover(self, task_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT test_cases_json FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row: return None, 0
        test_cases = json.loads(row[0])
        conn.close()

        print(f"[*] Starting 5s Discovery for Task: {task_id}")
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(5)

        start_time = time.time()
        try:
            # 1ステップ
            for p1 in self.primitives:
                dna = struct.pack("H", self.pid_to_int[p1])
                if self._verify(dna, test_cases):
                    signal.alarm(0)
                    self._persist_wisdom(task_id, dna)
                    return dna, time.time() - start_time
            
            # 2ステップ
            for p1 in self.primitives:
                for p2 in self.primitives:
                    dna = struct.pack("H", self.pid_to_int[p1]) + struct.pack("H", self.pid_to_int[p2])
                    if self._verify(dna, test_cases):
                        signal.alarm(0)
                        self._persist_wisdom(task_id, dna)
                        return dna, time.time() - start_time
            
            signal.alarm(0)
            return None, time.time() - start_time

        except TimeoutError:
            print(f"[!] {task_id}: Humble Failure (5s).")
            return "TIMEOUT", time.time() - start_time

    def _verify(self, dna, test_cases):
        try:
            for tc in test_cases:
                res = self.vm.execute_dna(dna, tc["input"])
                if abs(res - tc["output"]) > 1e-4: return False
            return True
        except: return False

    def _persist_wisdom(self, task_id, dna):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO wisdom (id, quantum_dna) VALUES (?, ?)", (task_id, dna))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    discovery = MorphicQuantumDiscovery()
    target_task = sys.argv[1]
    res_dna, elapsed = discovery.discover(target_task)
    if res_dna and res_dna != "TIMEOUT":
        print(f"[SUCCESS] {target_task} learned in {elapsed:.2f}s.")
