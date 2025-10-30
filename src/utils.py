import sys
import os

def resource_path(relative_path: str) -> str:
    """
    アセットへの絶対パスを取得する。
    開発環境(.py)とPyInstallerのワンフォルダモード(.exe)の両方で動作する。
    PyInstallerの_internalフォルダの存在も考慮する。
    """
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)

            internal_path = os.path.join(base_path, '_internal')
            if os.path.isdir(internal_path):
                base_path = internal_path
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        return os.path.join(base_path, relative_path)

    except Exception as e:
        print(f"Error getting resource path: {e}")
        return os.path.join('.', relative_path)