import os
import sys
import requests
import configparser
from tkinter import messagebox
from src import config
from src.utils import resource_path, is_admin, run_as_admin

def check_and_run_setup():
    """
    設定をチェックし、必要な場合は管理者権限を要求してセットアップを実行する。
    """
    parser = configparser.ConfigParser()
    parser.read(config.CONFIG_PATH)

    stored_version = parser.get('AppInfo', 'LastVersion', fallback=None)
    setup_complete = parser.getboolean('AppInfo', 'SetupComplete', fallback=False)

    # 1. セットアップや更新が必要なタスクをリストアップ
    tasks = []
    if stored_version != config.APP_VERSION:
        tasks.append("update")
    if not setup_complete:
        tasks.append("initial")
    
    # 2. 実行すべきタスクがなければ、ここで処理を終了
    if not tasks:
        return

    # 3. 管理者権限があるか確認
    if is_admin():
        # --- [権限あり] インストール処理を直接実行 ---
        try:
            if "update" in tasks:
                _install_obj_script()
                _update_config_file('LastVersion', config.APP_VERSION)
                messagebox.showinfo("スクリプト更新完了", "'@SekaiObjects.obj2' が正常に更新されました。")
            
            if "initial" in tasks:
                _install_anm_script()
                _update_config_file('SetupComplete', 'true')
                messagebox.showinfo("初回セットアップ完了", "'unmult.anm2', 'dkjson.lua' が正常にインストールされました。")
        
        except Exception as e:
            messagebox.showerror("セットアップ失敗", f"スクリプトのインストール中にエラーが発生しました:\n{e}")

    else:
        # --- [権限なし] ユーザーに管理者権限での再起動を促す ---
        msg = (
            "AviUtl用スクリプトのセットアップ（初回または更新）が必要です。\n\n"
            "この処理には管理者権限が必要です。\n"
            "アプリケーションを管理者として再起動しますか？"
        )
        if messagebox.askyesno("管理者権限が必要です", msg):
            run_as_admin()
            sys.exit(0) # 現在の通常権限のプロセスを終了させる
        else:
            messagebox.showwarning("セットアップのスキップ", "スクリプトのセットアップがスキップされました。\nAviUtl連携機能が正しく動作しない可能性があります。")


def _update_config_file(key: str, value: str):
    """設定ファイルを読み込み、指定されたキーと値を更新して保存する"""
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    parser = configparser.ConfigParser()
    parser.read(config.CONFIG_PATH)
    
    if 'AppInfo' not in parser:
        parser['AppInfo'] = {}
        
    parser['AppInfo'][key] = value
    
    with open(config.CONFIG_PATH, 'w') as f:
        parser.write(f)


# ( _check_write_permission, _install_obj_script, _install_anm_script は前の回答から変更なし )
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

def _install_obj_script():
    """@SekaiObjects.obj2 のバージョンを置換してインストールする"""
    src_path = resource_path(os.path.join("assets", "scripts", "@SekaiObjects.obj2"))
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
    """unmult.anm2, dkjson.luaをダウンロードしてインストールする"""
    dest_path = os.path.join(config.AVIUTL_SCRIPT_DIR, "unmult.anm2")
    response = requests.get(config.UNMULT_ANM_URL, timeout=15)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    
    dest_path = os.path.join(config.AVIUTL_SCRIPT_DIR, "dkjson.lua")
    response = requests.get(config.DKJSON_LUA_URL, timeout=15)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    
    print(f"'{dest_path}' へスクリプトをダウンロード・インストールしました。")