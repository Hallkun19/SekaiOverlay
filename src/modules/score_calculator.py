from src.config import WEIGHT_MAP
import json
import os
from typing import List, Dict, Any, Tuple


class BpmChange:
    def __init__(self, beat: float, bpm: float):
        self.beat = beat
        self.bpm = bpm

def _get_value_from_data(data: List[Dict[str, Any]], name: str) -> float:
    for item in data:
        if item.get("name") == name:
            return float(item.get("value", 0.0))
    return 0.0

def _get_time_from_bpm_changes(bpm_changes: List[BpmChange], beat: float) -> float:
    ret_time = 0.0
    for i, bpm_change in enumerate(bpm_changes):
        if i == len(bpm_changes) - 1:
            ret_time += (beat - bpm_change.beat) * (60 / bpm_change.bpm)
            break
        next_bpm_change = bpm_changes[i+1]
        if bpm_change.beat <= beat < next_bpm_change.beat:
            ret_time += (beat - bpm_change.beat) * (60 / bpm_change.bpm)
            break
        elif beat >= next_bpm_change.beat:
            ret_time += (next_bpm_change.beat - bpm_change.beat) * (60 / bpm_change.bpm)
        else:
            break
    return ret_time

def _calculate_score_frames(level_info: Dict[str, Any], level_data: Dict[str, Any], power: float) -> Tuple[List[Dict[str, Any]], float]:
    """スコア、コンボ、秒数、ランク、スコアバーのフレームリストを計算する"""
    rating = level_info.get("rating", 1)
    entities = level_data.get("entities", [])
    
    # 1. ランクとスコアバー計算の準備
    # レーティングを5-40の範囲にクランプ
    clamped_rating = max(5, min(rating, 40))
    
    # Goのロジックに基づきランク境界を計算
    rank_border = 1200000 + (clamped_rating - 5) * 4100
    rank_s = 1040000 + (clamped_rating - 5) * 5200
    rank_a = 840000 + (clamped_rating - 5) * 4200
    rank_b = 400000 + (clamped_rating - 5) * 2000
    rank_c = 20000 + (clamped_rating - 5) * 100

    # GoのscoreXv1（0.0～1.0の割合）に相当するバーの位置
    POS_BORDER = 1.0
    POS_S = 0.890
    POS_A = 0.742
    POS_B = 0.591
    POS_C = 0.447

    weighted_notes_count = sum(WEIGHT_MAP.get(e.get("archetype", ""), 0.0) for e in entities)
    if weighted_notes_count == 0:
        return [{"seconds": 0.0, "combo": 0, "score": 0, "add_score": 0, "rank": "d", "score_bar": 0.0}]

    bpm_changes: List[BpmChange] = []
    note_entities: List[Dict[str, Any]] = []

    for entity in entities:
        archetype = entity.get("archetype", "")
        if archetype == "#BPM_CHANGE" and entity.get("data"):
            beat = _get_value_from_data(entity["data"], "#BEAT")
            bpm = _get_value_from_data(entity["data"], "#BPM")
            if bpm > 0:
                bpm_changes.append(BpmChange(beat=beat, bpm=bpm))
        elif WEIGHT_MAP.get(archetype, 0.0) > 0.0 and entity.get("data"):
            note_entities.append(entity)

    bpm_changes.sort(key=lambda b: b.beat)
    note_entities.sort(key=lambda e: _get_value_from_data(e["data"], "#BEAT"))

    frames = [{"seconds": 0.0, "combo": 0, "score": 0, "add_score": 0, "rank": "none", "score_bar": 0.0}]
    level_fax = (rating - 5) * 0.005 + 1
    combo_fax = 1.0
    score = 0.0
    
    for i, entity in enumerate(note_entities):
        combo_counter = i + 1
        
        if combo_counter % 100 == 1 and combo_counter > 1:
            combo_fax += 0.01
        if combo_fax > 1.1:
            combo_fax = 1.1

        weight = WEIGHT_MAP.get(entity.get("archetype", ""), 0.0)
        
        add_score = (power / weighted_notes_count) * 4 * weight * 1 * level_fax * combo_fax * 1
        score += add_score
        
        beat = _get_value_from_data(entity["data"], "#BEAT")
        time = _get_time_from_bpm_changes(bpm_changes, beat)
        last_note_time = time
        
        # 2. ランクとスコアバーを計算
        rank = ""
        score_bar = 0.0
        
        # スコアを比較してランクとバーの位置を決定
        if score >= rank_border:
            rank = "s"
            score_bar = POS_BORDER
        elif score >= rank_s:
            rank = "s"
            score_bar = ((score - rank_s) / (rank_border - rank_s)) * (POS_BORDER - POS_S) + POS_S
        elif score >= rank_a:
            rank = "a"
            score_bar = ((score - rank_a) / (rank_s - rank_a)) * (POS_S - POS_A) + POS_A
        elif score >= rank_b:
            rank = "b"
            score_bar = ((score - rank_b) / (rank_a - rank_b)) * (POS_A - POS_B) + POS_B
        elif score >= rank_c:
            rank = "c"
            score_bar = ((score - rank_c) / (rank_b - rank_c)) * (POS_B - POS_C) + POS_C
        elif score == 0:
            rank = "none"
            score_bar = 0.0
        else:
            rank = "d"
            # rank_c が0になることはほぼないが、念のためチェック
            score_bar = (score / rank_c) * POS_C if rank_c > 0 else 0.0

        # 3. フレームデータを数値型で追加
        frames.append({
            "seconds": round(time, 6),
            "combo": combo_counter,
            "score": round(score),
            "add_score": round(add_score),
            "rank": rank,
            "score_bar": round(score_bar, 6)
        })
        
    return frames, last_note_time

def generate_skobj_data(level_id: str, assets_base_path: str, team_power: float, app_version: str) -> float:
    """
    譜面データを読み込み、スコアオブジェクトデータを計算してJSONファイルに出力する。
    """
    dist_dir = os.path.join("dist", level_id)
    level_info_path = os.path.join(dist_dir, "level.json")
    chart_path = os.path.join(dist_dir, "chart.json")
    
    try:
        with open(level_info_path, 'r', encoding='utf-8') as f:
            level_info = json.load(f)["item"]
        with open(chart_path, 'r', encoding='utf-8') as f:
            level_data = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"必要なファイルが見つかりません: {e.filename}")
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"JSONファイルの解析中にエラーが発生しました: {e}")

    print("スコアオブジェクトデータの生成を開始します...")
    
    score_frames, last_note_time = _calculate_score_frames(level_info, level_data, team_power)

    output_data = {
        "asset_path": assets_base_path + "\\",
        "version": app_version,
        "objects": score_frames
    }

    output_path = os.path.join(dist_dir, "skobj_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"スコアオブジェクトデータを '{output_path}' に保存しました。")
    return last_note_time