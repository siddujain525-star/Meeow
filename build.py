"""
Run this once to build cat.exe
Requires: pip install pyinstaller
"""
import subprocess
import sys
import os

def build():
    base = os.path.dirname(os.path.abspath(__file__))
    cat  = os.path.join(base, "cat.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # single .exe
        "--windowed",          # no console window
        "--name", "DesktopCat",
        "--icon", "NONE",
        cat
    ]

    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    print("\nBuilding DesktopCat.exe — this takes ~1 minute...")
    subprocess.run(cmd, check=True)

    exe = os.path.join(base, "dist", "DesktopCat.exe")
    if os.path.exists(exe):
        print(f"\n✓ Done! Your exe is at:\n  {exe}")
        print("\nYou can share this .exe with anyone — no Python needed.")
    else:
        print("\n✗ Build failed — check the output above for errors.")

    input("\nPress Enter to close...")

if __name__ == "__main__":
    build()
