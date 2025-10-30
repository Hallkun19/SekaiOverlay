import sys
import os

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