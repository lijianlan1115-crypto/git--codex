#!/usr/bin/env python3
from pathlib import Path
import argparse
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOS_DIR = ROOT / "repos"
DEFAULT_REPO = "hotel--ota-ai"


def run(args, cwd):
    result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="同步或查看本地 Git 代码库状态")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="repos 下的仓库名")
    parser.add_argument("--pull", action="store_true", help="执行 git pull --ff-only")
    args = parser.parse_args()

    repo_dir = (REPOS_DIR / args.repo).resolve()
    if not repo_dir.exists():
        raise SystemExit(f"仓库不存在: {repo_dir}")

    print(f"仓库: {repo_dir}")
    run(["git", "status", "--short"], repo_dir)
    run(["git", "log", "-5", "--oneline"], repo_dir)

    if args.pull:
        run(["git", "pull", "--ff-only"], repo_dir)


if __name__ == "__main__":
    main()
