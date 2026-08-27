import os
import subprocess


def create_desktop_shortcut() -> bool:
    """
    Creates or updates a Windows desktop shortcut for cswap-widget.
    Returns True if successful, False otherwise.
    """
    try:
        # Determine package / project root directory
        current_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        run_script = os.path.join(project_root, "run.py")

        vbs_content = f'''
Set ws = CreateObject("WScript.Shell")
desktopPath = ws.SpecialFolders("Desktop")
Set shortcut = ws.CreateShortcut(desktopPath & "\\cswap Widget.lnk")
shortcut.TargetPath = "pythonw.exe"
shortcut.Arguments = """{run_script}"""
shortcut.WorkingDirectory = """{project_root}"""
shortcut.WindowStyle = 7
shortcut.IconLocation = "shell32.dll, 15"
shortcut.Save
'''
        vbs_file = os.path.join(project_root, "make_shortcut.vbs")
        with open(vbs_file, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        subprocess.run(["cscript", "//nologo", vbs_file], check=True)
        if os.path.exists(vbs_file):
            os.remove(vbs_file)
        return True
    except Exception as e:
        print(f"Kısayol oluşturulurken hata: {e}")
        return False
