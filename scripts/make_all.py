import glob
import os
import subprocess
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    pattern = os.path.join(script_dir, "make_*.py")
    scripts = sorted(glob.glob(pattern))

    self_path = os.path.abspath(__file__)
    scripts = [s for s in scripts if os.path.abspath(s) != self_path]

    if not scripts:
        print("No make_*.py scripts found.")
        return

    failed = []
    for script in scripts:
        print(f"-> Running {os.path.basename(script)} ...")
        result = subprocess.run([sys.executable, script], cwd=repo_root)
        if result.returncode != 0:
            print(f"   FAILED (exit code {result.returncode})")
            failed.append(script)
        else:
            print(f"   OK")

    if failed:
        print(f"\n{len(failed)} script(s) failed:")
        for s in failed:
            print(f"  {os.path.basename(s)}")
        sys.exit(1)
    else:
        print(f"\nAll {len(scripts)} script(s) completed successfully.")

if __name__ == "__main__":
    main()
