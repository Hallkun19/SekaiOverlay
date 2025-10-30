import os
from typing import Callable
from src.modules import downloader, image_processor, score_calculator, alias_writer
from src import config

class Generator:
    def __init__(self, config: dict, status_callback: Callable[[str], None]):
        self.config = config
        self.update_status = status_callback
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def run(self):
        """全ての生成処理を実行する"""
        full_level_id = ""
        try:
            full_level_id_input = self.config['full_level_id']
            if '-' not in full_level_id_input:
                raise ValueError("無効な譜面ID形式です (例: chcy-test-1)。")
            prefix, id_part = full_level_id_input.rsplit('-', 1)
            print(f"prefix: {prefix}, id_part: {id_part}")
            
            self.update_status(f"[{full_level_id_input}] データをダウンロード中...")
            full_level_id = downloader.download_and_prepare_assets(prefix, id_part)

            self.update_status("背景画像を生成中...")
            image_processor.generate_background_image(full_level_id, self.config['bg_version'])

            self.update_status("スコアオブジェクトを生成中...")
            assets_path = os.path.join(self.script_dir, "assets")
            last_note_time = score_calculator.generate_skobj_data(
                full_level_id, assets_path, self.config['team_power'], config.APP_VERSION
            )

            self.update_status("エイリアスオブジェクトを生成中...")
            alias_writer.generate_alias_object(
                full_level_id, last_note_time, self.config['extra_data']
            )

            self._cleanup(full_level_id)
            
            self.update_status("すべての処理が正常に完了しました。")
            return True, f"譜面 '{full_level_id}' のファイル生成が完了しました。"

        except Exception as e:
            self.update_status(f"エラー: {e}")
            return False, f"処理中にエラーが発生しました:\n{e}"

    def _cleanup(self, full_level_id: str):
        self.update_status("一時ファイルをクリーンアップ中...")
        dist_dir = os.path.join(self.script_dir, "dist", full_level_id)
        for filename in ["level.json", "chart.json"]:
            path = os.path.join(dist_dir, filename)
            if os.path.exists(path):
                os.remove(path)