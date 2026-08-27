import os
import sys
import subprocess

script_dir = os.path.abspath(os.path.dirname(__file__))
widget_path = os.path.join(script_dir, "widget.py")

vbs_content = f'''
Set ws = CreateObject("WScript.Shell")
desktopPath = ws.SpecialFolders("Desktop")
Set shortcut = ws.CreateShortcut(desktopPath & "\\cswap Widget.lnk")
shortcut.TargetPath = "pythonw.exe"
shortcut.Arguments = """{widget_path}"""
shortcut.WorkingDirectory = """{script_dir}"""
shortcut.WindowStyle = 7
shortcut.IconLocation = "shell32.dll, 15"
shortcut.Save
'''

vbs_file = os.path.join(script_dir, "make_shortcut.vbs")
with open(vbs_file, "w", encoding="utf-8") as f:
    f.write(vbs_content)

subprocess.run(["cscript", "//nologo", vbs_file])
if os.path.exists(vbs_file):
    os.remove(vbs_file)
print("Masaüstü kısayolu başarıyla oluşturuldu / güncellendi!")

