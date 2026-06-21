#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="让 Codex 根据需求修改本地 Git 代码库并生成测试预警报告")
    parser.add_argument("--repo", default=server.DEFAULT_REPO_NAME, help="repos 下的仓库名或绝对路径")
    parser.add_argument("--requirement", required=True, help="需求变更说明")
    parser.add_argument("--files", nargs="*", default=[], help="建议关注文件")
    args = parser.parse_args()

    repo_dir = server.resolve_repo_dir(args.repo)
    before_status = server.git_status(repo_dir)
    recent_log = server.git_recent_log(repo_dir)
    prompt = server.build_apply_prompt(args.requirement, args.files, recent_log, before_status)

    codex_result = server.call_codex_cli(prompt, repo_dir, mode="apply", timeout=600)
    actual_diff = server.git_worktree_diff(repo_dir)
    actual_files = server.git_changed_files(repo_dir)

    payload = server.build_payload(
        "需求变更实现与测试预警报告",
        repo_dir,
        {
            "mode": "cli-apply",
            "repo": str(repo_dir),
            "requirement": args.requirement,
            "files": actual_files or args.files,
            "before_status": before_status,
            "diff_preview": server.truncate_text(actual_diff, 800),
        },
        actual_diff,
        actual_files or args.files,
        args.requirement,
        codex_result,
    )

    patch_path = server.OUTPUTS_DIR / "codex_patch.diff"
    patch_path.write_text(actual_diff, encoding="utf-8")
    payload["outputs"]["patch"] = str(patch_path)
    print(json.dumps(payload["outputs"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
