import os
import sys 
import subprocess
from typing import Callable
from src.modules import downloader, image_processor, score_calculator, alias_writer
from src import config
from src.utils import get_app_root

class Generator:
    def __init__(self, config: dict, status_callback: Callable[[str], None]):
        self.config = config
        self.update_status = status_callback
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app_root = get_app_root()

    def run(self):
        """全ての生成処理を実行する"""
        full_level_id = ""
        try:
            full_level_id_input = self.config['full_level_id']
            if '-' not in full_level_id_input:
                raise ValueError("無効な譜面ID形式です (例: chcy-test-1)。")
            prefix, id_part = self.config['full_level_id'].rsplit('-', 1)
            full_level_id = f"{prefix}-{id_part}"

            # ★ 出力先ディレクトリのフルパスをここで一元管理
            dist_dir = os.path.join(self.app_root, "dist", full_level_id)

            # 2. ダウンロード (★ dist_dirを渡す)
            self.update_status(f"[{full_level_id}] データをダウンロード中...")
            downloader.download_and_prepare_assets(prefix, id_part, dist_dir)

            # 3. 背景画像生成 (★ dist_dirを渡す)
            self.update_status("背景画像を生成中...")
            image_processor.generate_background_image(full_level_id, self.config['bg_version'], dist_dir)

            # 4. スコアオブジェクト生成 (★ dist_dirを渡す)
            self.update_status("スコアオブジェクトを生成中...")
            last_note_time = score_calculator.generate_skobj_data(
                full_level_id, dist_dir, self.config['team_power'], config.APP_VERSION
            )

            # 5. エイリアスオブジェクト生成 (★ dist_dirを渡す)
            self.update_status("エイリアスオブジェクトを生成中...")
            alias_writer.generate_alias_object(
                full_level_id, dist_dir, last_note_time, self.config['extra_data']
            )

            # 6. クリーンアップ (★ dist_dirを使う)
            self._cleanup(dist_dir)

            self.update_status("出力フォルダを開いています...")
            self._open_output_folder(dist_dir)
            
            self.update_status("すべての処理が正常に完了しました。")
            return True, f"譜面 '{full_level_id}' のファイル生成が完了しました。"

        except Exception as e:
            self.update_status(f"エラー: {e}")
            return False, f"処理中にエラーが発生しました:\n{e}"

    def _cleanup(self, dist_dir: str):
        self.update_status("一時ファイルをクリーンアップ中...")
        for filename in ["level.json", "chart.json"]:
            path = os.path.join(dist_dir, filename)
            if os.path.exists(path):
                os.remove(path)
    def _open_output_folder(self, path: str):
        """
        指定されたパスをシステムのファイルエクスプローラーで開く。
        Windows, macOS, Linuxに対応。
        """
        try:
            if sys.platform == "win32":
                # Windowsの場合
                os.startfile(os.path.normpath(path))
            elif sys.platform == "darwin":
                # macOSの場合
                subprocess.run(["open", path])
            else:
                # Linuxの場合
                subprocess.run(["xdg-open", path])
        except Exception as e:
            # フォルダを開けなくても処理全体は成功しているので、エラーにはしない
            print(f"出力フォルダを自動で開けませんでした: {e}")