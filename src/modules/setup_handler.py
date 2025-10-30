import os
import requests
import configparser
from tkinter import messagebox
from src import config
from src.utils import resource_path

def check_and_run_setup():
    """
    設定ファイルをチェックし、必要に応じてスクリプトのセットアップや更新を行う。
    """
    parser = configparser.ConfigParser()
    parser.read(config.CONFIG_PATH)

    stored_version = parser.get('AppInfo', 'LastVersion', fallback=None)
    setup_complete = parser.getboolean('AppInfo', 'SetupComplete', fallback=False)

    if stored_version != config.APP_VERSION:
        msg = (
            f"アプリケーションのバージョンが新しくなりました (v{config.APP_VERSION})。\n\n"
            "AviUtlで正しく動作するために、対応するスクリプト '@SekaiObjects.obj2' を更新します。\n"
            "よろしいですか？"
        )
        if messagebox.askyesno("スクリプト更新", msg):
            try:
                if not _check_write_permission(config.AVIUTL_SCRIPT_DIR):
                    raise PermissionError(f"'{config.AVIUTL_SCRIPT_DIR}' への書き込み権限がありません。\n管理者として再起動してください。")
                
                _install_obj_script()
                _update_config_file('LastVersion', config.APP_VERSION)
                messagebox.showinfo("更新完了", "'@SekaiObjects.obj2' が正常に更新されました。")

            except Exception as e:
                messagebox.showerror("更新失敗", f"スクリプトの更新中にエラーが発生しました:\n{e}")

    if not setup_complete:
        msg_anm = (
            "これは初回起動、または関連ファイルのセットアップが未完了です。\n\n"
            "AviUtlの動作に必要なスクリプト 'unmult.anm2' をダウンロードし、インストールします。\n"
            "よろしいですか？"
        )
        if messagebox.askyesno("初回セットアップ", msg_anm):
            try:
                if not _check_write_permission(config.AVIUTL_SCRIPT_DIR):
                    raise PermissionError(f"'{config.AVIUTL_SCRIPT_DIR}' への書き込み権限がありません。\n管理者として再起動してください。")

                _install_anm_script()
                _update_config_file('SetupComplete', 'true')
                messagebox.showinfo("成功", "'unmult.anm2' が正常にインストールされました。")

            except Exception as e:
                messagebox.showerror("セットアップ失敗", f"スクリプトのインストール中にエラーが発生しました:\n{e}")
        else:
            # 拒否された場合でも、次回はバージョン更新のチェックのみ行うように設定
            _update_config_file('SetupComplete', 'true')


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
    """unmult.anm2 をダウンロードしてインストールする"""
    dest_path = os.path.join(config.AVIUTL_SCRIPT_DIR, "unmult.anm2")
    response = requests.get(config.UNMULT_ANM_URL, timeout=15)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    print(f"'{dest_path}' へスクリプトをダウンロード・インストールしました。")