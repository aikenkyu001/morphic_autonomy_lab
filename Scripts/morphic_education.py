import json
import time
import os
import subprocess
import sys

class MorphicEducation:
    def __init__(self):
        self.lab_root = "/private/test/morphic_autonomy_lab"
        self.memory_path = f"{self.lab_root}/Knowledge/interaction_memory.json"
        self.discovered_path = f"{self.lab_root}/Knowledge/discovered_wisdom.json"
        self.tasks_dir = f"{self.lab_root}/Tasks"
        self.synthesizer = f"{self.lab_root}/Scripts/morphic_synthesizer.py"

    def record_interaction(self, human_input, projected_logic):
        interaction = {
            "timestamp": time.time(),
            "human_instruction": human_input,
            "projected_logic": projected_logic,
            "status": "educated"
        }
        with open(self.memory_path, 'a') as f:
            f.write(json.dumps(interaction) + "\n")

    def teach_and_verify(self, task_name, nl_logic):
        print(f"Education: Teaching logic for {task_name}...")
        
        # 1. .nl ファイルの作成
        nl_path = f"{self.tasks_dir}/{task_name}_educated.nl"
        with open(nl_path, 'w') as f:
            f.write(nl_logic)
            
        # 2. 合成 (独立したプロセスで solution.py を生成)
        try:
            subprocess.run([sys.executable, self.synthesizer, nl_path], check=True, capture_output=True, cwd=self.tasks_dir)
        except subprocess.CalledProcessError as e:
            print(f"Synthesis failed: {e.stderr.decode()}")
            return False

        # 3. 検証 (独立したプロセスで実行)
        # 検証用のワンライナーを作成
        verify_code = f"""
import sys, os, json, inspect, importlib, importlib.util
sys.path.append('{self.lab_root}')
from Scripts.VM.python.evaluator import VError

# 課題のロード
with open('{self.tasks_dir}/{task_name}.json', 'r') as f:
    task = json.load(f)

# 最新の solution.py をインポート (ユニーク名)
module_name = '{task_name}_educated_solution'
spec = importlib.util.spec_from_file_location(module_name, os.path.join('{self.tasks_dir}', f'{{module_name}}.py'))
solution_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solution_mod)
sol = solution_mod.Solution()

method_name = task["interface"].split("(")[0]
sig = inspect.signature(getattr(sol, method_name))
num_params = len([p for p in sig.parameters.values() if p.name != 'self'])

all_passed = True
for tc in task["test_cases"]:
    if num_params > 1 and isinstance(tc["input"], list):
        res = getattr(sol, method_name)(*tc["input"])
    else:
        res = getattr(sol, method_name)(tc["input"])
    
    if isinstance(res, VError):
        print(f"VM Error: {{res.message}}")
        sys.exit(1)
    if res != tc["output"]:
        print(f"Mismatch: Expected {{tc['output']}}, got {{res}}")
        sys.exit(1)
sys.exit(0)
"""
        try:
            # 独立したプロセスで検証を実行
            res = subprocess.run([sys.executable, "-c", verify_code], capture_output=True, text=True, cwd=self.tasks_dir)
            if res.returncode == 0:
                print(f"Verification SUCCESS! The logic taught by Human is correct.")
                # 成功した知識の保存
                result = {
                    "task": task_name,
                    "logic": nl_logic,
                    "educated": True,
                    "timestamp": time.time()
                }
                with open(self.discovered_path, 'a') as df:
                    df.write(json.dumps(result) + "\n")
                return True
            else:
                print(f"Verification FAILED:\n{res.stdout}\n{res.stderr}")
                return False
        except Exception as e:
            print(f"Process execution error during verification: {e}")
            return False

if __name__ == "__main__":
    # 互換性のためのメインブロック (既存の呼び出し元を壊さない)
    if len(sys.argv) > 1:
        edu = MorphicEducation()
        # 引数があればそれを使うロジック (必要に応じて拡張)
