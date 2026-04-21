#!/usr/bin/env python3
import os
import shutil
import argparse
from logger import log_operation

def install_hermes(target_path):
    source_path = "dist/hermes"
    if not os.path.exists(source_path):
        log_operation("install_hermes", "ERROR", "Build not found")
        print(f"ERROR: Build not found at {source_path}. Run build_platform.py first.")
        return

    print(f"Installing Hermes resources to {target_path}...")
    try:
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        log_operation("install_hermes", "SUCCESS", f"Target: {target_path}")
        print("SUCCESS: Installation complete.")
    except Exception as e:
        log_operation("install_hermes", "ERROR", f"Target: {target_path} | Error: {str(e)}")
        print(f"ERROR: Installation failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install built Hermes resources to a destination.")
    parser.add_argument("--target", help="Destination path (default: ~/.hermes/resources)", default=os.path.expanduser("~/.hermes/resources"))
    
    args = parser.parse_args()
    
    install_hermes(args.target)
 Josephson
