# alias_gen.py

import os
import json
from src.utils import resource_path


def generate_alias_object(level_id: str, dist_dir: str, last_note_time: float, extra_data: dict) -> str: # ★ base_dir引数を削除
    print("エイリアスオブジェクトの生成を開始します...")
    
    # ★ プロジェクトルートを基準にパスを再構築
    assets_dir = resource_path('assets')
    
    try:
        # ★ template_pathをresource_pathで取得
        template_path = resource_path(os.path.join('assets', 'alias', 'template.object'))
        level_json_path = os.path.join(dist_dir, 'level.json')
        output_path = os.path.join(dist_dir, 'main.object')

        # 2. ファイル読み込み
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        with open(level_json_path, 'r', encoding='utf-8') as f:
            level_data = json.load(f)
        
        # 3. プレースホルダー用の値を取得
        item_data = level_data.get('item', {})
        
        final_title = extra_data.get('title') or item_data.get('title') or '-'
        final_author = extra_data.get('author') or item_data.get('author') or '-'
        
        difficulty_input = extra_data.get('difficulty', 'custom')
        standard_difficulties = ["easy", "normal", "hard", "expert", "master", "append"]
        difficulty_img_val = difficulty_input.lower() if difficulty_input.lower() in standard_difficulties else 'custom'
        vocal_input = extra_data.get('vocal')
        vocal_text = f"Vo. {vocal_input}" if vocal_input else "Inst. ver."

        replacements = {
            '{title}': final_title,
            '{author}': final_author,
            '{words}': extra_data.get('words', '-'),
            '{music}': extra_data.get('music', '-'),
            '{arrange}': extra_data.get('arrange', '-'),
            '{vocal}': vocal_text,
            '{difficulty}': difficulty_input.upper(),
            '{difficulty_img}': difficulty_img_val
        }
        
        # 空白だった場合のデフォルト値を設定
        for key, value in replacements.items():
            if not value:
                if key == '{vocal}':
                    replacements[key] = 'Inst. ver.'
                else:
                    replacements[key] = '-'

        # パス情報
        dist_full_path = os.path.abspath(dist_dir).replace(os.sep, '\\')
        assets_full_path = os.path.abspath(assets_dir).replace(os.sep, '\\')
        replacements['{distPath}'] = dist_full_path
        replacements['{assetsPath}'] = assets_full_path

        # 4. 新しいフレーム計算ロジック
        video_start_frame = round((last_note_time + 1.0) * 60) + 316
        fade_start_frame = video_start_frame + 161
        fade_stop_frame = fade_start_frame + 142
        end_frame = fade_stop_frame + 124

        replacements['{videoStartFrame}'] = str(video_start_frame)
        replacements['{fadeStartFrame}'] = str(fade_start_frame)
        replacements['{fadeStopFrame}'] = str(fade_stop_frame)
        replacements['{endFrame}'] = str(end_frame)
        
        # 5. 文字列を一括置換
        output_content = template_content
        for placeholder, value in replacements.items():
            output_content = output_content.replace(placeholder, value)

        # 6. 結果を書き出し
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"エイリアスオブジェクトを '{output_path}' に保存しました。")
        return final_title

    except FileNotFoundError as e:
        raise FileNotFoundError(f"必要なファイルが見つかりませんでした: {e.filename}")
    except Exception as e:
        raise RuntimeError(f"エイリアスオブジェクトの生成中にエラーが発生しました: {e}")