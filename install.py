import os
import sys
import winreg

def install():
    # Get the directory where this script lives
    base = os.path.dirname(os.path.abspath(__file__))
    cat_path = os.path.join(base, "cat.py")
    python_exe = sys.executable

    # The command that runs the cat
    command = f'"{python_exe}" "{cat_path}"'

    # Write to Windows registry Run key
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "DesktopCat", 0, winreg.REG_SZ, command)
    winreg.CloseKey(key)
    print("✓ Desktop Cat will now start automatically with Windows.")
    print(f"  Running: {command}")

def uninstall():
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    try:
        winreg.DeleteValue(key, "DesktopCat")
        print("✓ Desktop Cat removed from startup.")
    except FileNotFoundError:
        print("Desktop Cat was not in startup.")
    winreg.CloseKey(key)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        uninstall()
    else:
        install()
    input("Press Enter to close...")
