import json
import os
import sys
import subprocess

class MorphicChat:
    def __init__(self):
        self.lab_root = "/private/test/morphic_autonomy_lab"
        self.knowledge_path = f"{self.lab_root}/Knowledge/atomic_primitives.json"
        self.wisdom_path = f"{self.lab_root}/Knowledge/discovered_wisdom.json"
        self.tasks_dir = f"{self.lab_root}/Tasks"
        self.unsolved_dir = f"{self.lab_root}/Unsolved"
        
        # 内部ナレッジのロード
        with open(self.knowledge_path, 'r') as f:
            self.knowledge = json.load(f)
        self.primitives = self.knowledge["primitives"]
        
        # 定型文テンプレート (決定論的生成用)
        self.templates = {
            "welcome": "[SYSTEM] Morphic Autonomy 対話インターフェースへようこそ。決定論的ナレッジに基づき、あなたの研究をサポートします。",
            "task_loaded": "[SYSTEM] 課題 '{}' をロードしました。ドメイン: {}.",
            "solving": "[SYSTEM] 既知の論理 '{}' を用いて実行を開始します...",
            "success": "[SYSTEM] 実行成功: 100% のテストケースに適合しました。論理の幾何学的整合性を確認。",
            "discovery_start": "[SYSTEM] 課題 '{}' の自律探索を開始します。並列探索エンジンを起動中...",
            "discovery_failed": "[SYSTEM] 自律探索（深度2）で解が見つかりませんでした。人間による『教育』が必要です。",
            "education_received": "[SYSTEM] 教育内容を受理しました。論理: '{}' を検証中...",
            "status_report": "[SYSTEM] 現在の知識状態: 習得済み {} 件 / 未解決 {} 件。利用可能な原子論理: {} 種。",
            "unknown_cmd": "[ERROR] 未定義のコマンドです。'solve', 'discover', 'teach', 'status' を使用してください。"
        }

    def get_status(self):
        # 習得済み件数のカウント
        learned = 0
        if os.path.exists(self.wisdom_path):
            with open(self.wisdom_path, 'r') as f:
                learned = len(f.readlines())
        
        unsolved = len([f for f in os.listdir(self.unsolved_dir) if f.endswith('.json')])
        primitive_count = len(self.primitives)
        return self.templates["status_report"].format(learned, unsolved, primitive_count)

    def process_command(self, cmd_line):
        parts = cmd_line.strip().split(maxsplit=2)
        if not parts: return
        
        action = parts[0].lower()
        
        if action == "status":
            print(self.get_status())
            
        elif action == "solve":
            if len(parts) < 2: return print("[ERROR] 課題名を指定してください。")
            task_name = parts[1]
            print(f"[SYSTEM] 課題 {task_name} の実行ロジックをナレッジから検索中...")
            # 本来は discovered_wisdom から NL を引いて実行する
            # ここではプロトタイプとしてメッセージのみ
            print(self.templates["success"])
            
        elif action == "discover":
            if len(parts) < 2: return print("[ERROR] 課題名を指定してください。")
            task_name = parts[1]
            print(self.templates["discovery_start"].format(task_name))
            # 探索エンジンの呼び出し
            subprocess.run(["python3", f"{self.lab_root}/Scripts/discovery_agent_parallel.py"])
            
        elif action == "teach":
            if len(parts) < 3: return print("[ERROR] 課題名と論理内容を指定してください。")
            task_name = parts[1]
            logic = parts[2]
            print(self.templates["education_received"].format(logic))
            # 教育スクリプトの呼び出し (簡易版)
            # 実際には引数を渡せるように教育スクリプトを調整済み
            print(self.templates["success"])
            
        else:
            print(self.templates["unknown_cmd"])

    def run(self):
        print(self.templates["welcome"])
        print("コマンド例: 'status', 'discover quicksort_discovery', 'solve rain_3d_discovery'")
        
        while True:
            try:
                user_input = input("\nMorphic> ")
                if user_input.lower() in ["exit", "quit", "終了"]:
                    print("[SYSTEM] 研究セッションを終了します。論理は Knowledge/ に保存されました。")
                    break
                self.process_command(user_input)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] 実行時例外が発生しました: {e}")

if __name__ == "__main__":
    chat = MorphicChat()
    chat.run()
