import os
import json
import itertools
import subprocess
import time
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

# 独立性を保つため、VM へのパスを通す
sys.path.append("/private/test/morphic_autonomy_lab/Scripts")

class DiscoveryAgentParallel:
    def __init__(self):
        self.lab_root = "/private/test/morphic_autonomy_lab"
        self.knowledge_path = f"{self.lab_root}/Knowledge/atomic_primitives.json"
        self.tasks_dir = f"{self.lab_root}/Tasks"
        self.unsolved_dir = f"{self.lab_root}/Unsolved"
        self.log_file = f"{self.lab_root}/Logs/learning_trace.log"
        self.discovered_path = f"{self.lab_root}/Knowledge/discovered_wisdom.json"
        self.synthesizer = f"{self.lab_root}/Scripts/morphic_synthesizer.py"
        
        with open(self.knowledge_path, 'r') as f:
            self.knowledge = json.load(f)
        
        self.primitives = self.knowledge["primitives"]
        self.output_patterns = self.knowledge["output_patterns"]["EN"]

    def log(self, message: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{ts}] {message}\n")

    def generate_nl(self, task_name, interface, steps, output_pattern):
        nl = f"TASK: {task_name}\nINTERFACE: {interface}\n\nLOGIC:\n  INPUT: arg1\n"
        for i, p_id in enumerate(steps, 1):
            label = self.primitives[p_id]["en_label"]
            nl += f"  {i}. {label}\n"
        nl += f"  OUTPUT: {output_pattern}\n"
        return nl

    @staticmethod
    def verify_static(task_json, nl_content, lab_root, synthesizer):
        # 並列実行用の静的メソッド
        task_name = task_json["task"]
        # プロセスIDをファイル名に含めて競合を避ける
        pid = os.getpid()
        temp_dir = f"{lab_root}/Tasks/tmp_{pid}"
        os.makedirs(temp_dir, exist_ok=True)
        
        nl_path = f"{temp_dir}/{task_name}.nl"
        with open(nl_path, 'w') as f:
            f.write(nl_content)
            
        try:
            # 合成 (solution.py を生成)
            subprocess.run(["python3", synthesizer, nl_path], check=True, capture_output=True, cwd=temp_dir)
            
            # テスト実行
            sys.path.insert(0, temp_dir)
            if 'solution' in sys.modules: del sys.modules['solution']
            from solution import Solution
            sol = Solution()
            
            all_passed = True
            method_name = task_json["interface"].split("(")[0]
            for tc in task_json["test_cases"]:
                actual = getattr(sol, method_name)(tc["input"])
                if actual != tc["output"]:
                    all_passed = False
                    break
            
            sys.path.pop(0)
            # 成功した場合は一時ディレクトリを消さずに残す（後で確認するため）か、情報を返す
            return all_passed, nl_content
        except Exception:
            return False, None
        finally:
            # クリーンアップ（失敗時はディレクトリを削除）
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def solve_task_parallel(self, task_file, max_workers=8):
        with open(f"{self.tasks_dir}/{task_file}", 'r') as f:
            task = json.load(f)
        
        self.log(f"Starting parallel discovery for {task['task']}")
        print(f"Target Task: {task['task']}")
        
        p_ids = list(self.primitives.keys())
        out_labels = list(self.output_patterns.keys())
        
        found = False
        for length in range(1, 3): # まずは短階層から
            self.log(f"Searching length {length}...")
            print(f"Exploring logic depth: {length}...")
            
            candidates = []
            for steps in itertools.product(p_ids, repeat=length):
                for out in out_labels:
                    nl = self.generate_nl(task["task"], task["interface"], steps, out)
                    candidates.append(nl)
            
            print(f"Generated {len(candidates)} candidates. Verifying in parallel...")
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.verify_static, task, nl, self.lab_root, self.synthesizer) for nl in candidates]
                for future in as_completed(futures):
                    success, nl_content = future.result()
                    if success:
                        self.log(f"SUCCESS! Logic found for {task['task']}")
                        print(f"SUCCESS! Logical Shape discovered for {task['task']}")
                        
                        result = {
                            "task": task["task"],
                            "logic": nl_content,
                            "timestamp": time.time(),
                            "method": "parallel_exhaustive"
                        }
                        with open(self.discovered_path, 'a') as df:
                            df.write(json.dumps(result) + "\n")
                        found = True
                        # 他のタスクをキャンセルするために直ちに抜ける
                        executor.shutdown(wait=False, cancel_futures=True)
                        return True
            if found: break
        
        if not found:
            self.log(f"FAILED to discover logic for {task['task']}")
            print(f"Reached discovery limit for {task['task']}. Moving to Unsolved.")
            with open(f"{self.unsolved_dir}/{task['task']}.json", 'w') as f:
                json.dump(task, f, indent=2)
        return found

if __name__ == "__main__":
    agent = DiscoveryAgentParallel()
    for f in os.listdir(agent.tasks_dir):
        if f.endswith(".json") and "discovery" in f:
            agent.solve_task_parallel(f)
