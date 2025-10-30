# src/modules/setup_handler.py

import os
import shutil
import requests
import configparser
from tkinter import messagebox
from src import config

def run_initial_setup():
    """初回起動時に必要なセットアップを実行する"""
    if os.path.exists(config.CONFIG_PATH):
        return # 設定ファイルがあれば初回ではないので何もしない

    # 1. ユーザーに同意を求める
    msg = (
        "これは初回起動です。AviUtlの動作に必要なスクリプトをセットアップしますか？\n\n"
        f"以下の処理が実行されます:\n"
        f"1. '@SekaiObjects.obj2' を '{config.AVIUTL_SCRIPT_DIR}' へコピー\n"
        f"2. 'unmult.anm2' をダウンロードし、同フォルダへコピー\n\n"
        "※この処理には管理者権限が必要になる場合があります。"
    )
    if not messagebox.askyesno("初回起動セットアップ", msg):
        _create_config_file() # セットアップしなくても次回から表示しないように設定ファイルを作成
        return

    # 2. 管理者権限（書き込み権限）をチェック
    if not _check_write_permission(config.AVIUTL_SCRIPT_DIR):
        messagebox.showerror("権限エラー", f"'{config.AVIUTL_SCRIPT_DIR}' への書き込み権限がありません。\nアプリケーションを右クリックし、「管理者として実行」で再起動してください。")
        return

    # 3. セットアップ処理の実行
    try:
        os.makedirs(config.AVIUTL_SCRIPT_DIR, exist_ok=True)
        
        # @SekaiObjects.obj2 のバージョンを置換してコピー
        _install_obj_script()
        
        # unmult.anm2 をダウンロードしてコピー
        _install_anm_script()

        messagebox.showinfo("成功", "スクリプトのセットアップが完了しました。")

    except Exception as e:
        messagebox.showerror("セットアップ失敗", f"スクリプトのインストール中にエラーが発生しました:\n{e}")
    finally:
        _create_config_file() # 成功・失敗にかかわらず設定ファイルを作成

def _check_write_permission(path: str) -> bool:
    """指定されたパスへの書き込み権限があるかチェックする"""
    try:
        os.makedirs(path, exist_ok=True)
        temp_file = os.path.join(path, 'temp_permission_check.tmp')
        with open(temp_file, 'w') as f:
            f.write('test')
        os.remove(temp_file)
        return True
    except (PermissionError, OSError):
        return False

def _create_config_file():
    """セットアップ完了のフラグとなる設定ファイルを作成する"""
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    parser = configparser.ConfigParser()
    parser['DEFAULT'] = {'SetupComplete': 'true'}
    with open(config.CONFIG_PATH, 'w') as f:
        parser.write(f)

def _install_obj_script():
    """@SekaiObjects.obj2 のバージョンを置換してインストールする"""
    src_path = os.path.join("assets", "scripts", "@SekaiObjects.obj2")
    dest_path = os.path.join(config.AVIUTL_SCRIPT_DIR, "@SekaiObjects.obj2")
    
    with open(src_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 9行目 (インデックス8) を書き換える
    if len(lines) >= 9:
        lines[8] = f'SKOBJ_VERSION = "{config.APP_VERSION}"\n'

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"'{dest_path}' へスクリプトをインストールしました。")

def _install_anm_script():
    """unmult.anm2 をダウンロードしてインストールする"""
    dest_path = os.path.join(config.AVIUTL_SCRIPT_DIR, "unmult.anm2")
    response = requests.get(config.UNMULT_ANM_URL, timeout=15)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    print(f"'{dest_path}' へスクリプトをダウンロード・インストールしました。")