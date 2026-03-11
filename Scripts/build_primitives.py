import json
import os

def build_atomic_primitives():
    src_path = "/private/test/morphic_autonomy_lab/Knowledge/semantic_dictionary.json"
    dst_path = "/private/test/morphic_autonomy_lab/Knowledge/atomic_primitives.json"
    
    with open(src_path, 'r') as f:
        data = json.load(f)
    
    primitives = {}
    arity_map = data["ARITY"]
    en_names = data["EN"]
    jp_names = data["JP"]
    
    # 逆引きマップの作成
    en_to_id = {v: k for k, v in en_names.items()}
    jp_to_id = {v: k for k, v in jp_names.items()}
    
    for p_id, arity in arity_map.items():
        primitives[p_id] = {
            "id": p_id,
            "arity": arity,
            "en_label": en_to_id.get(p_id, p_id),
            "jp_label": jp_to_id.get(p_id, p_id)
        }
    
    output_patterns = data["OUTPUT_PATTERNS"]
    
    atomic_data = {
        "primitives": primitives,
        "output_patterns": output_patterns
    }
    
    with open(dst_path, 'w') as f:
        json.dump(atomic_data, f, indent=2, ensure_ascii=False)
    print(f"Created atomic primitives at {dst_path}")

if __name__ == "__main__":
    build_atomic_primitives()
