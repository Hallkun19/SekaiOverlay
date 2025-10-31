import sys
import os
import ctypes

def get_app_root() -> str:
    """
    アプリケーションのルートパスを取得する。
    開発環境(.py)とPyInstaller(.exe)の両方で動作する。
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def resource_path(relative_path: str) -> str:
    """
    アセットへの絶対パスを取得する。（読み込み専用）
    """
    base_path = get_app_root()
    if getattr(sys, 'frozen', False):
        internal_path = os.path.join(base_path, '_internal')
        if os.path.isdir(internal_path):
            base_path = internal_path
    
    return os.path.join(base_path, relative_path)

def is_admin() -> bool:
    """
    現在のプロセスが管理者権限で実行されているかを確認します (Windows専用)。
    """
    if sys.platform == "win32":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return False

def run_as_admin():
    """
    アプリケーションを管理者権限で再起動します (Windows専用)。
    UACプロンプトが表示されます。
    """
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )
        except Exception as e:
            print(f"管理者権限での再起動に失敗しました: {e}")