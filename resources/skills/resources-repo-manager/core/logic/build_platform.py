#!/usr/bin/env python3
import os
import shutil
import argparse
from logger import log_operation

def build_hermes():
    print("Building for Hermes...")
    dist_path = "dist/hermes"
    try:
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
        os.makedirs(dist_path)

        # 1. Copy contexts (templates)
        print("  Adding contexts...")
        shutil.copytree("contexts/hermes", os.path.join(dist_path, "contexts"))

        # 2. Process resources with hermes platform overlay
        print("  Adding resources with Hermes overlays...")
        res_root = "resources"
        for category in os.listdir(res_root):
            cat_path = os.path.join(res_root, category)
            if not os.path.isdir(cat_path): continue
            
            for res_id in os.listdir(cat_path):
                res_path = os.path.join(cat_path, res_id)
                overlay_path = os.path.join(res_path, "platforms/hermes")
                
                # If it has a Hermes overlay, we prioritize it or include it
                if os.path.exists(overlay_path):
                    target_res_path = os.path.join(dist_path, "resources", category, res_id)
                    os.makedirs(target_res_path, exist_ok=True)
                    # Simple copy of core + hermes overlay
                    shutil.copytree(os.path.join(res_path, "core"), os.path.join(target_res_path, "core"), dirs_exist_ok=True)
                    shutil.copytree(overlay_path, target_res_path, dirs_exist_ok=True)
        
        log_operation("build_platform", "SUCCESS", "Platform: hermes")
        print(f"SUCCESS: Hermes build complete in {dist_path}")
    except Exception as e:
        log_operation("build_platform", "ERROR", f"Platform: hermes | Error: {str(e)}")
        print(f"ERROR: Build failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build platform-specific distributions.")
    parser.add_argument("--platform", required=True, choices=['hermes', 'albert', 'openclaw'], help="Target platform")
    
    args = parser.parse_args()
    
    if args.platform == 'hermes':
        build_hermes()
    else:
        print(f"Build for {args.platform} is not yet implemented.")
