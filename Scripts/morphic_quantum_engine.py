import sqlite3
import json
import struct
import re

class MorphicQuantumEngine:
    def __init__(self, db_path="Database/morphic_autonomy.db"):
        self.db_path = db_path
        self._load_lexicon_maps()

    def _load_lexicon_maps(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, label_en, integer_id FROM lexicon")
        rows = cursor.fetchall()
        self.label_to_id = {}
        self.id_to_label = {}
        for row in rows:
            cid, label_en, int_id = row
            # コードIDを優先
            self.label_to_id[cid.lower()] = int_id
            if label_en:
                self.label_to_id[label_en.lower()] = int_id
            self.id_to_label[int_id] = cid
        conn.close()

    def ast_to_quantum_dna(self, logic_content):
        if not logic_content: return b""
        if isinstance(logic_content, str):
            try: logic_content = json.loads(logic_content)
            except: pass

        dna = bytearray()
        # ラベルを長い順に
        sorted_labels = sorted(self.label_to_id.keys(), key=len, reverse=True)

        # ステップ行を抽出する正規表現 (例: "1. calculate distance")
        steps = []
        if isinstance(logic_content, list):
            steps = logic_content
        else:
            # "1. ...", "2. ..." の行だけを抽出
            steps = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', logic_content)
        
        for step in steps:
            step_norm = step.lower().strip()
            # プリミティブ名との完全一致または部分一致を丁寧に探す
            found = False
            for label in sorted_labels:
                # 単語境界を意識したチェック (例: "mul" が "multiplication" に含まれないように)
                if re.search(rf'\b{re.escape(label)}\b', step_norm.replace("_", " ")):
                    dna.extend(struct.pack("H", self.label_to_id[label]))
                    found = True
                    break
            
            # フォールバック: 単純な部分一致
            if not found:
                for label in sorted_labels:
                    if label in step_norm.replace("_", " "):
                        dna.extend(struct.pack("H", self.label_to_id[label]))
                        break
        return bytes(dna)

    def quantum_dna_to_ast(self, dna):
        if not dna: return []
        ids = []
        for i in range(0, len(dna), 2):
            integer_id = struct.unpack("H", dna[i:i+2])[0]
            ids.append(self.id_to_label.get(integer_id, f"UNKNOWN_{integer_id}"))
        return ids

    def update_wisdom_with_dna(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, logic_json FROM wisdom")
        rows = cursor.fetchall()
        for task_id, logic_json in rows:
            dna = self.ast_to_quantum_dna(logic_json)
            cursor.execute("UPDATE wisdom SET quantum_dna = ? WHERE id = ?", (dna, task_id))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    engine = MorphicQuantumEngine()
    engine.update_wisdom_with_dna()
    # 検証
    for tid in ["matrix_product_determinant", "distance_formula", "quadratic_discriminant"]:
        conn = sqlite3.connect("Database/morphic_autonomy.db")
        row = conn.execute("SELECT quantum_dna FROM wisdom WHERE id = ?", (tid,)).fetchone()
        if row and row[0]:
            print(f"DNA for {tid}: {engine.quantum_dna_to_ast(row[0])}")
        conn.close()
