import os, sys, re, json

class MorphicSynthesizer:
    def __init__(self):
        # ラボの環境に合わせてパスを絶対指定
        self.lab_root = "/Users/miyata.fumio/Projects/morphic_autonomy_lab"
        dict_path = os.path.join(self.lab_root, "Knowledge/atomic_primitives.json")
        with open(dict_path, "r") as f: 
            self.dictionary = json.load(f)
        
        # 内部構造を整理
        self.arity_map = {p["id"]: p["arity"] for p in self.dictionary["primitives"].values()}
        
        # フレーズのソート (最長一致)
        phrases = []
        for p in self.dictionary["primitives"].values():
            if p["en_label"]: phrases.append((p["en_label"], p["id"]))
            if p["jp_label"]: phrases.append((p["jp_label"], p["id"]))
        self.sorted_phrases = sorted(phrases, key=lambda x: len(x[0]), reverse=True)
        
        self.output_patterns = {
            **self.dictionary["output_patterns"]["JP"],
            **self.dictionary["output_patterns"]["EN"]
        }

    def synthesize_from_nl(self, nl_text):
        methods_code = []
        blocks = nl_text.split("---")
        wisdom_path = os.path.join(self.lab_root, "Knowledge", "wisdom_base.json")

        for block in blocks:
            if not block.strip(): continue
            
            # インターフェース名の抽出
            method_match = re.search(r"(?:INTERFACE|interface|インターフェース):\s*(\w+)\(", block)
            method_name = method_match.group(1) if method_match else "solve"
            
            # 入力変数の抽出
            input_match = re.search(r"(?:INPUT|input|入力):\s*(.*)", block)
            input_vars = [v.strip() for v in input_match.group(1).split(",")] if input_match else ["arg1"]

            found_builtins = []
            for line in block.splitlines():
                line_stripped = line.strip()
                if not line_stripped: continue
                # ヘッダー行をスキップ
                if ":" in line_stripped and not re.match(r"^\d+\.", line_stripped): continue

                for phrase, builtin in self.sorted_phrases:
                    if phrase.lower() in line.lower():
                        found_builtins.append(builtin)
                        break

            if not found_builtins: continue

            # AST の構築 (多引数対応・カリー化形式・パイプライン連鎖)
            def build_ast_code(funcs, vars):
                # 入力変数のリスト
                available_vars = list(vars)
                last_result_ast = None
                
                for f in funcs:
                    arity = self.arity_map.get(f, 1)
                    func_ast = f"Var('{f}')"
                    
                    # 引数の適用
                    for i in range(arity):
                        if i == 0 and last_result_ast:
                            # 2ステップ目以降の最初の引数は、前のステップの結果
                            func_ast = f"App({func_ast}, {last_result_ast})"
                        elif available_vars:
                            # それ以外は入力変数を使用
                            v = available_vars.pop(0)
                            func_ast = f"App({func_ast}, Var('{v}'))"
                        else:
                            # 引数が足りない場合は Literal(None)
                            func_ast = f"App({func_ast}, Literal(None))"
                    
                    last_result_ast = func_ast
                return last_result_ast

            logic_ast_code = build_ast_code(found_builtins, input_vars)
            
            # 出力パターンの決定
            output_logic = "return res.value"
            for phrase, pattern in self.output_patterns.items():
                if phrase in block:
                    output_logic = pattern
                    break
            
            env_bind = ", ".join([f"'{v}': VLiteral({v})" for v in input_vars])
            # 重要: evaluate() に渡すのは文字列ではなく、生成された AST オブジェクトそのもの
            methods_code.append(f"""    def {method_name}(self, {', '.join(input_vars)}):
        from Scripts.VM.python.evaluator import Evaluator, VLiteral, VError
        vm = Evaluator('{wisdom_path}')
        # AST をコードとして直接展開
        expr = {logic_ast_code}
        res = vm.evaluate(expr, {{{env_bind}}})
        if isinstance(res, VError): return res
        {output_logic}""")

        if not methods_code: return None
        
        # インポートパスの調整
        full_code = f"""import sys, os
sys.path.append('{self.lab_root}')
from Scripts.VM.python.morphic_ast import Literal, Var, App, Let, Lambda, ListNode, TreeNode
from Scripts.VM.python.evaluator import Evaluator, VLiteral, VError

class Solution:
""" + "\n".join(methods_code)
        return full_code

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    nl_path = sys.argv[1]
    with open(nl_path, "r") as f: nl_text = f.read()
    
    syn = MorphicSynthesizer()
    code = syn.synthesize_from_nl(nl_text)
    
    if code:
        # 入力ファイル名に基づいたユニークなファイル名を作成
        base_name = os.path.basename(nl_path).replace(".nl", "")
        # Tasks/ 内に生成されるように調整
        out_path = os.path.join(os.path.dirname(nl_path), "solution.py")
        with open(out_path, "w") as f: f.write(code)
        print(f"Synthesized: {out_path}")
    else:
        print("Failed to synthesize logic.")
        sys.exit(1)
