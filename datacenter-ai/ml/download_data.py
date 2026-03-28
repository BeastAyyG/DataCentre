import os
import sys
import subprocess
from pathlib import Path

RAW_DIR = Path(__file__).parent / "data" / "raw"
OMNI_DIR = RAW_DIR / "OmniAnomaly"

def main():
    print("=" * 60)
    print("Data Center AI — Dataset Downloader")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if OMNI_DIR.exists():
        print(f"Directory {OMNI_DIR} already exists. Skipping clone.")
    else:
        print(f"Cloning OmniAnomaly repository...")
        try:
            subprocess.check_call(
                ["git", "clone", "https://github.com/NetManAIOps/OmniAnomaly.git", str(OMNI_DIR)]
            )
            print("Successfully cloned OmniAnomaly repository.")
        except Exception as e:
            print(f"ERROR downloading dataset: {e}")
            sys.exit(1)

    smd_dir = OMNI_DIR / "ServerMachineDataset"
    
    if smd_dir.exists():
        print(f"\nServerMachineDataset located at: {smd_dir}")
        print("Data download complete.")
    else:
        print(f"\nWARNING: ServerMachineDataset not found in {OMNI_DIR}.")

    print("=" * 60)

if __name__ == "__main__":
    main()
