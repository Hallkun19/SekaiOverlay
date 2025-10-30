import os
import sys
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image


def _morph(image_pil: Image.Image, target_coords: List[Tuple[int, int]], target_size: Tuple[int, int]) -> Image.Image:
    # 1. ターゲット座標のバウンディングボックスを計算
    min_x = min(p[0] for p in target_coords)
    min_y = min(p[1] for p in target_coords)
    max_x = max(p[0] for p in target_coords)
    max_y = max(p[1] for p in target_coords)
    bbox_w, bbox_h = int(max_x - min_x), int(max_y - min_y)

    if bbox_w <= 0 or bbox_h <= 0:
        return Image.new("RGBA", target_size, (0, 0, 0, 0))

    # 2. 元画像をバウンディングボックスのサイズにリサイズ
    resized_pil = image_pil.resize((bbox_w, bbox_h), Image.Resampling.NEAREST)

    # Pillow -> OpenCV 形式 (RGBA -> BGRA)
    resized_cv = cv2.cvtColor(np.array(resized_pil), cv2.COLOR_RGBA2BGRA)
    src_h, src_w, _ = resized_cv.shape
    src_points = np.float32([[0, 0], [src_w, 0], [0, src_h], [src_w, src_h]])

    # 3. 射影変換のための座標を計算（バウンディングボックスの左上を原点とする相対座標）
    relative_target_coords = np.float32([
        (p[0] - min_x, p[1] - min_y) for p in target_coords
    ])

    # 4. 射影変換行列を計算し、ワープを実行
    matrix = cv2.getPerspectiveTransform(src_points, relative_target_coords)
    projected_cv = cv2.warpPerspective(resized_cv, matrix, (bbox_w, bbox_h))

    # OpenCV -> Pillow 形式 (BGRA -> RGBA)
    projected_pil = Image.fromarray(cv2.cvtColor(projected_cv, cv2.COLOR_BGRA2RGBA))

    # 5. 最終的な出力用画像に、計算した位置へ貼り付け
    final_image = Image.new("RGBA", target_size, (0, 0, 0, 0))
    final_image.paste(projected_pil, (int(min_x), int(min_y)))

    return final_image


def _mask(image_pil: Image.Image, mask_pil: Image.Image) -> Image.Image:
    if image_pil.mode != 'RGBA':
        image_pil = image_pil.convert('RGBA')
    if mask_pil.mode != 'RGBA':
        mask_pil = mask_pil.convert('RGBA')

    # NumPy配列に変換してアルファチャンネルを操作
    image_alpha = np.array(image_pil.getchannel('A'))
    mask_alpha = np.array(mask_pil.getchannel('A'))

    # 両者のアルファチャンネルの各ピクセルの最小値をとる
    new_alpha_np = np.minimum(image_alpha, mask_alpha)
    new_alpha_pil = Image.fromarray(new_alpha_np, mode='L')

    # 元の画像に新しいアルファチャンネルを設定
    result_pil = image_pil.copy()
    result_pil.putalpha(new_alpha_pil)
    return result_pil


def _render_v3(target_image: Image.Image, assets_dir: str) -> Image.Image:
    """v3の背景画像を生成します。"""
    # アセット画像の読み込み
    base = Image.open(os.path.join(assets_dir, "base.png")).convert("RGBA")
    bottom = Image.open(os.path.join(assets_dir, "bottom.png")).convert("RGBA")
    center_cover = Image.open(os.path.join(assets_dir, "center_cover.png")).convert("RGBA")
    center_mask = Image.open(os.path.join(assets_dir, "center_mask.png")).convert("RGBA")
    side_cover = Image.open(os.path.join(assets_dir, "side_cover.png")).convert("RGBA")
    side_mask = Image.open(os.path.join(assets_dir, "side_mask.png")).convert("RGBA")
    windows = Image.open(os.path.join(assets_dir, "windows.png")).convert("RGBA")

    base_size = base.size
    
    # サイドジャケットの生成
    side_jackets = Image.new("RGBA", base_size)
    left_normal = _morph(target_image, [(566, 161), (1183, 134), (633, 731), (1226, 682)], base_size)
    right_normal = _morph(target_image, [(966, 104), (1413, 72), (954, 525), (1390, 524)], base_size)
    left_mirror = _morph(target_image, [(633, 1071), (1256, 1045), (598, 572), (1197, 569)], base_size)
    right_mirror = _morph(target_image, [(954, 1122), (1393, 1167), (942, 702), (1366, 717)], base_size)

    side_jackets = Image.alpha_composite(side_jackets, left_normal)
    side_jackets = Image.alpha_composite(side_jackets, right_normal)
    side_jackets = Image.alpha_composite(side_jackets, left_mirror)
    side_jackets = Image.alpha_composite(side_jackets, right_mirror)
    side_jackets = Image.alpha_composite(side_jackets, side_cover)

    # センタージャケットの生成
    center = Image.new("RGBA", base_size)
    center_normal = _morph(target_image, [(824, 227), (1224, 227), (833, 608), (1216, 608)], base_size)
    center_mirror = _morph(target_image, [(830, 1017), (1214, 1017), (833, 676), (1216, 676)], base_size)
    
    center = Image.alpha_composite(center, center_normal)
    center = Image.alpha_composite(center, center_mirror)
    center = Image.alpha_composite(center, center_cover)

    # マスキング処理
    side_jackets = _mask(side_jackets, side_mask)
    center = _mask(center, center_mask)

    # 最終的な合成
    final_image = base.copy()
    final_image = Image.alpha_composite(final_image, side_jackets)
    final_image = Image.alpha_composite(final_image, side_cover)
    final_image = Image.alpha_composite(final_image, windows)
    final_image = Image.alpha_composite(final_image, center)
    final_image = Image.alpha_composite(final_image, bottom)

    return final_image

def _render_v1(target_image: Image.Image, assets_dir: str) -> Image.Image:
    """v1の背景画像を生成します。"""
    # アセット画像の読み込み
    base = Image.open(os.path.join(assets_dir, "base.png")).convert("RGBA")
    side_mask = Image.open(os.path.join(assets_dir, "side_mask.png")).convert("RGBA")
    center_mask = Image.open(os.path.join(assets_dir, "center_mask.png")).convert("RGBA")
    mirror_mask = Image.open(os.path.join(assets_dir, "mirror_mask.png")).convert("RGBA")
    frames = Image.open(os.path.join(assets_dir, "frames.png")).convert("RGBA")
    
    base_size = base.size

    # サイドジャケットの生成
    side_jackets = Image.new("RGBA", base_size)
    left_normal = _morph(target_image, [(449, 114), (1136, 99), (465, 804), (1152, 789)], base_size)
    right_normal = _morph(target_image, [(1018, 92), (1635, 51), (1026, 756), (1630, 740)], base_size)

    side_jackets = Image.alpha_composite(side_jackets, left_normal)
    side_jackets = Image.alpha_composite(side_jackets, right_normal)
    
    # センタージャケットの生成
    center = Image.new("RGBA", base_size)
    center_normal = _morph(target_image, [(798, 193), (1252, 193), (801, 635), (1246, 635)], base_size)
    center_mirror = _morph(target_image, [(798, 1152), (1252, 1152), (795, 713), (1252, 713)], base_size)

    # マスキング処理
    center_normal = _mask(center_normal, center_mask)
    center_mirror = _mask(center_mirror, mirror_mask)
    
    center = Image.alpha_composite(center, center_normal)
    center = Image.alpha_composite(center, center_mirror)

    side_jackets = _mask(side_jackets, side_mask)

    # 最終的な合成
    final_image = base.copy()
    final_image = Image.alpha_composite(final_image, side_jackets)
    final_image = Image.alpha_composite(final_image, center)
    final_image = Image.alpha_composite(final_image, frames)

    return final_image


def generate_background_image(level_id: str, version: str) -> None:
    """
    背景画像とカバー画像を合成して新しい画像を生成します。
    """
    print("背景画像の生成を開始します...")

    # パス設定
    dist_dir = os.path.join("dist", level_id)
    assets_dir = os.path.join("assets", "background", f"v{version}")
    cover_image_path = os.path.join(dist_dir, "jacket.jpg")
    output_image_path = os.path.join(dist_dir, "background.png")

    try:
        # カバー画像を読み込み
        target_image = Image.open(cover_image_path).convert("RGBA")
        
        # バージョンに応じてレンダリング関数を呼び出し
        if version == "3":
            final_image = _render_v3(target_image, assets_dir)
        elif version == "1":
            final_image = _render_v1(target_image, assets_dir)
        else:
            raise ValueError(f"バージョン '{version}' は現在サポートされていません。")

        # 生成した画像を保存
        final_image.save(output_image_path, "PNG")
        print(f"背景画像を '{output_image_path}' に保存しました。")

    except FileNotFoundError as e:
        raise FileNotFoundError(f"画像ファイルが見つかりませんでした: {e.filename}")
    except Exception as e:
        raise RuntimeError(f"背景画像の生成中に予期せぬエラーが発生しました: {e}")