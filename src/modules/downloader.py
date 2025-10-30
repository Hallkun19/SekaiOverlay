import requests
import os
import gzip
import shutil
import json
from PIL import Image
from src.config import SERVER_MAP

def download_and_prepare_assets(prefix: str, id_part: str, dist_dir: str) -> str:
    """
    指定サーバーから譜面データをダウンロードし、ジャケットをリサイズする。
    成功した場合、完全な譜面IDを返す。
    """
    base_url = SERVER_MAP.get(prefix)
    if not base_url:
        raise ValueError(f"サポートされていないサーバー接頭辞です: {prefix}")

    api_url = f"{base_url}{prefix}-{id_part}"
    full_level_id = f"{prefix}-{id_part}"
    
    print(f"APIにアクセスしています: {api_url}")
    response = requests.get(api_url, timeout=15)
    response.raise_for_status()
    api_response_data = response.json()

    os.makedirs(dist_dir, exist_ok=True)
    
    with open(os.path.join(dist_dir, "level.json"), 'w', encoding='utf-8') as f:
        json.dump(api_response_data, f, indent=4)

    print(f"ファイルを '{dist_dir}' に保存します。")
    item = api_response_data.get("item", {})
    
    _download_file(item["cover"]["url"], os.path.join(dist_dir, "jacket.jpg"))
    _resize_jacket(os.path.join(dist_dir, "jacket.jpg"))
    _download_file(item["bgm"]["url"], os.path.join(dist_dir, "music.mp3"))
    
    chart_gz_path = os.path.join(dist_dir, "chart.json.gz")
    _download_file(item["data"]["url"], chart_gz_path)
    _unzip_gz(chart_gz_path, os.path.join(dist_dir, "chart.json"))
    
    return full_level_id

def _download_file(url: str, dest_path: str):
    with requests.get(url, stream=True, timeout=15) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def _resize_jacket(image_path: str, size: tuple[int, int] = (512, 512)):
    with Image.open(image_path).convert("RGB") as img:
        if img.size != size:
            print(f"  -> jacket.jpgを{size[0]}x{size[1]}にリサイズしています...")
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            resized_img.save(image_path, "jpeg", quality=95)

def _unzip_gz(gz_path: str, dest_path: str):
    with gzip.open(gz_path, 'rb') as f_in:
        with open(dest_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)