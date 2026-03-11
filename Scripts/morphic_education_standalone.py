import json, os, time, sys, subprocess

class MorphicEducationStandalone:
    def __init__(self):
        self.lab_root = "/private/test/morphic_autonomy_lab"
        self.scripts_dir = f"{self.lab_root}/Scripts"

    def run_education_task(self, task_name, nl_logic, instr):
        # 独立したプロセスとして教育スクリプトを呼び出す
        # 1回ごとに Python インスタンスを起動するため、キャッシュ汚染が発生しない
        script_code = f"""
import json, os, sys, time, inspect, importlib.util
sys.path.append('{self.scripts_dir}')
from morphic_education import MorphicEducation

edu = MorphicEducation()
task_name = '{task_name}'
nl_logic = {repr(nl_logic)}
instr = '{instr}'

edu.record_interaction(instr, [task_name])
if edu.teach_and_verify(task_name, nl_logic):
    print(f'SUCCESS: {{task_name}}')
    sys.exit(0)
else:
    print(f'FAILED: {{task_name}}')
    sys.exit(1)
"""
        try:
            result = subprocess.run([sys.executable, "-c", script_code], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Process execution error: {e}")
            return False

if __name__ == "__main__":
    edu_standalone = MorphicEducationStandalone()
    
    challenges = [
        {
            "name": "matrix_det_2x2_univ",
            "nl": "TASK: matrix_det_2x2_univ\\nINTERFACE: solveDet2x2(self, matrix)\\n\\nLOGIC:\\n  INPUT: matrix\\n  1. calculate 2x2 determinant\\n  OUTPUT: return value\\n",
            "instr": "Calculate 2x2 matrix determinant."
        },
        {
            "name": "matrix_det_3x3_univ",
            "nl": "TASK: matrix_det_3x3_univ\\nINTERFACE: solveDet3x3(self, matrix)\\n\\nLOGIC:\\n  INPUT: matrix\\n  1. calculate 3x3 determinant\\n  OUTPUT: return value\\n",
            "instr": "Calculate 3x3 matrix determinant using Sarrus rule."
        }
    ]

    print("--- University Math: Standalone Process Education ---")
    for c in challenges:
        edu_standalone.run_education_task(c["name"], c["nl"], c["instr"])
